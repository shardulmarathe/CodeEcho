"""Tracks estimated API spend against daily caps.

Two layers of protection, both reset at UTC midnight:

  1. A GLOBAL daily cap (``api_budget_cap_usd``) — the hard backstop on total
     estimated LLM spend across everyone.
  2. A PER-SUBJECT daily cap — a single user/guest-IP can only spend so much,
     so one caller can't drain the global cap and lock everyone else out.
     The subject is resolved per request (see ``services/usage.py``).

Either cap can be set to 0 (or negative) to mean UNLIMITED for that scope. The
per-subject caps ship unlimited: the upstream LLM key has no billing attached, so
throttling individual users buys nothing that per-IP rate limiting (see
``services/ratelimit.py``) doesn't already buy. The global cap stays on as a
circuit breaker against a runaway loop, not as a per-user quota.

Storage:
  - When Supabase is configured (production), spend is tracked DURABLY in the
    ``api_usage_daily`` table (one row per (day, subject)). This is required on
    ephemeral-disk / restart-prone hosts (e.g. Render): a local file would reset
    to zero on every restart and silently defeat the cap. Increments are atomic
    via the ``increment_api_usage`` RPC.
  - When Supabase is NOT configured (local/offline dev), spend falls back to a
    single date-bucketed JSON file, written atomically and serialized with a
    threading.Lock (correct for a single-process server). Run one worker in that
    mode, or the file is per-process.

Public API (unchanged — many call sites depend on it):
  get_budget_status(), check_budget(), record_cost(),
  estimate_gemini_cost(), estimate_embedding_cost().
"""

import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models import BudgetStatus
from app.services import supabase_client, usage

# Rough pricing estimates (USD per 1K tokens), per model. Flash is the historical ledger
# baseline; pro is scaled to the public flash:pro ratio (~4x in, ~4x out) so switching the
# scoring model to pro doesn't silently undercount spend against the $3/day Stanford cap.
GEMINI_COST_PER_1K_INPUT_TOKENS = 0.0001  # default (flash) — kept for back-compat
GEMINI_COST_PER_1K_OUTPUT_TOKENS = 0.0004
GEMINI_TEXT_PRICING = {
    "gemini-2.5-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.5-pro": {"input": 0.000417, "output": 0.0016},
}
_DEFAULT_TEXT_PRICING = {
    "input": GEMINI_COST_PER_1K_INPUT_TOKENS,
    "output": GEMINI_COST_PER_1K_OUTPUT_TOKENS,
}
# Embeddings: local model is free ($0); Google text-embedding-004 ~$0.02/1M tokens
EMBEDDING_COST_PER_1M_TOKENS = 0.02
# Azure OpenAI Whisper transcription ~$0.006 / audio-minute
WHISPER_COST_PER_MINUTE = 0.006

# The row key for total spend across everyone in the durable store.
GLOBAL_SUBJECT = "global"

LEDGER_PATH = Path("./data/budget_ledger.json")  # local-fallback only
_MAX_ENTRIES = 500  # keep the local ledger file bounded
_lock = threading.Lock()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _unlimited(cap: float) -> bool:
    """A cap of 0 (or negative) disables that scope's limit entirely."""
    return cap <= 0


def _cap_for_subject(subject: str) -> float:
    if subject.startswith("user:"):
        return settings.user_daily_cap_usd
    return settings.guest_daily_cap_usd  # ip:<addr> (guest / anon)


def _status_from_spent(spent: float) -> BudgetStatus:
    cap = settings.api_budget_cap_usd
    if _unlimited(cap):
        # cap_usd <= 0 is the wire signal for "no cap"; remaining is meaningless.
        return BudgetStatus(
            cap_usd=cap, spent_usd=round(spent, 4), remaining_usd=0.0, budget_exceeded=False
        )
    return BudgetStatus(
        cap_usd=cap,
        spent_usd=round(spent, 4),
        remaining_usd=round(max(0.0, cap - spent), 4),
        budget_exceeded=spent >= cap,
    )


# --- Supabase-backed store (production) -------------------------------------

def _sb_spent(client, day: str, subject: str) -> float:
    rows = (
        client.table("api_usage_daily")
        .select("spent_usd")
        .eq("day", day)
        .eq("subject", subject)
        .limit(1)
        .execute()
        .data
    )
    if rows:
        return float(rows[0].get("spent_usd") or 0.0)
    return 0.0


def _sb_increment(client, day: str, subject: str, cost: float) -> float:
    """Atomically add ``cost`` to (day, subject) and return the new total."""
    res = client.rpc(
        "increment_api_usage",
        {"p_day": day, "p_subject": subject, "p_cost": cost},
    ).execute()
    data = res.data
    if isinstance(data, list):
        data = data[0] if data else 0.0
    return float(data or 0.0)


# --- local JSON store (offline fallback) ------------------------------------

def _fresh(day: str) -> dict:
    return {"date": day, "global_spent_usd": 0.0, "subjects": {}, "entries": []}


def _load_ledger_for_today() -> dict:
    """Load the local ledger, resetting it if it's from a previous day."""
    day = _today()
    if LEDGER_PATH.exists():
        try:
            ledger = json.loads(LEDGER_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            ledger = _fresh(day)
        if ledger.get("date") != day or "global_spent_usd" not in ledger:
            ledger = _fresh(day)
    else:
        ledger = _fresh(day)
    ledger.setdefault("subjects", {})
    ledger.setdefault("entries", [])
    return ledger


def _save_ledger(ledger: dict) -> None:
    """Atomically replace the local ledger file so a crash mid-write can't corrupt it."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(LEDGER_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(ledger, f, indent=2)
        os.replace(tmp, LEDGER_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --- public API -------------------------------------------------------------

def get_budget_status() -> BudgetStatus:
    if supabase_client.is_configured():
        try:
            spent = _sb_spent(supabase_client.get_client(), _today(), GLOBAL_SUBJECT)
            return _status_from_spent(spent)
        except Exception:
            pass  # transient Supabase error — degrade to the local view below
    with _lock:
        return _status_from_spent(_load_ledger_for_today()["global_spent_usd"])


def check_budget() -> None:
    """Raise ``BudgetExceededError`` if the global OR this subject's daily cap is hit."""
    subject = usage.get_subject()

    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            day = _today()
            if not _unlimited(settings.api_budget_cap_usd) and (
                _sb_spent(client, day, GLOBAL_SUBJECT) >= settings.api_budget_cap_usd
            ):
                raise BudgetExceededError(
                    f"Daily API budget cap of ${settings.api_budget_cap_usd:.2f} reached "
                    f"for today. Try again tomorrow.",
                    scope="global",
                )
            if subject:
                cap = _cap_for_subject(subject)
                if not _unlimited(cap) and _sb_spent(client, day, subject) >= cap:
                    raise BudgetExceededError(
                        f"Your daily usage limit of ${cap:.2f} has been reached. "
                        f"Try again tomorrow.",
                        scope="subject",
                    )
            return
        except BudgetExceededError:
            raise
        except Exception:
            pass  # transient Supabase error — fall back to the local ledger

    with _lock:
        ledger = _load_ledger_for_today()
        if not _unlimited(settings.api_budget_cap_usd) and (
            ledger["global_spent_usd"] >= settings.api_budget_cap_usd
        ):
            raise BudgetExceededError(
                f"Daily API budget cap of ${settings.api_budget_cap_usd:.2f} reached "
                f"for today. Try again tomorrow.",
                scope="global",
            )
        if subject:
            cap = _cap_for_subject(subject)
            if not _unlimited(cap) and ledger["subjects"].get(subject, 0.0) >= cap:
                raise BudgetExceededError(
                    f"Your daily usage limit of ${cap:.2f} has been reached. "
                    f"Try again tomorrow.",
                    scope="subject",
                )


def record_cost(service: str, description: str, cost_usd: float) -> BudgetStatus:
    subject = usage.get_subject()

    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            day = _today()
            global_spent = _sb_increment(client, day, GLOBAL_SUBJECT, cost_usd)
            if subject:
                _sb_increment(client, day, subject, cost_usd)
            return _status_from_spent(global_spent)
        except Exception:
            pass  # transient Supabase error — record locally instead of losing it

    with _lock:
        ledger = _load_ledger_for_today()
        ledger["global_spent_usd"] = round(ledger["global_spent_usd"] + cost_usd, 6)
        if subject:
            ledger["subjects"][subject] = round(
                ledger["subjects"].get(subject, 0.0) + cost_usd, 6
            )
        ledger["entries"].append(
            {
                "service": service,
                "description": description,
                "cost_usd": round(cost_usd, 6),
                "subject": subject,
            }
        )
        if len(ledger["entries"]) > _MAX_ENTRIES:
            ledger["entries"] = ledger["entries"][-_MAX_ENTRIES:]
        _save_ledger(ledger)
        return _status_from_spent(ledger["global_spent_usd"])



def estimate_whisper_cost(duration_sec: float) -> float:
    return (duration_sec / 60.0) * WHISPER_COST_PER_MINUTE


def _text_pricing_for_model(model: Optional[str]) -> dict:
    """Per-1K-token rates for a Gemini text model. Unknown/blank -> flash default;
    any '...pro...' model maps to pro pricing."""
    if not model:
        return _DEFAULT_TEXT_PRICING
    key = model.strip().lower()
    for name, rates in GEMINI_TEXT_PRICING.items():
        if key.startswith(name):
            return rates
    if "pro" in key:
        return GEMINI_TEXT_PRICING["gemini-2.5-pro"]
    return _DEFAULT_TEXT_PRICING


def estimate_gemini_cost(
    input_tokens: int, output_tokens: int, model: Optional[str] = None
) -> float:
    rates = _text_pricing_for_model(model)
    return (input_tokens / 1000) * rates["input"] + (output_tokens / 1000) * rates["output"]


def cost_of_call(result, prompt: str, model: Optional[str] = None) -> float:
    """Cost of one LLM call, from the provider's own token counts when available.

    ``result`` is an ``llm_client.LLMResult``; its ``output_tokens`` already folds
    in reasoning tokens, which bill at the output rate.

    Falls back to the historical word-count heuristic only when the provider
    reported no usage at all. That heuristic is bad in a direction that matters --
    it cannot see thinking tokens, so a scoring call (pro, 2048-token thinking
    budget) was undercounted on every single scorecard. Prefer real counts.
    """
    input_tokens = getattr(result, "input_tokens", None)
    output_tokens = getattr(result, "output_tokens", None)
    if input_tokens is None or output_tokens is None:
        text = getattr(result, "text", "") or ""
        input_tokens = int(len(prompt.split()) * 1.3)
        output_tokens = int(len(text.split()) * 1.3)
    return estimate_gemini_cost(input_tokens, output_tokens, model=model)


def estimate_embedding_cost(tokens: int) -> float:
    """Cost of embedding `tokens`. Zero for the local model; small for Google."""
    return (tokens / 1_000_000) * EMBEDDING_COST_PER_1M_TOKENS


class BudgetExceededError(Exception):
    def __init__(self, message: str, scope: str = "global") -> None:
        super().__init__(message)
        self.scope = scope  # "global" | "subject"
