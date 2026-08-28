"""Unified LLM client — routes to the correct provider."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from openai import OpenAI

from app.config import settings


@dataclass
class LLMResult:
    """A completion plus the provider's own token accounting.

    ``output_tokens`` INCLUDES reasoning/thinking tokens where the provider
    reports them separately: they are billed at the output rate, and scoring runs
    with a real thinking budget, so folding them in is the whole point of
    carrying usage around instead of estimating from the response text.

    Both counts are None when the provider didn't report usage; callers fall
    back to a word-count estimate via ``budget.cost_of_call``.
    """

    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    @property
    def metered(self) -> bool:
        return self.input_tokens is not None and self.output_tokens is not None

UIT_GATEWAY_URL = "https://aiapi-prod.stanford.edu/v1"
STANFORD_LLM_GEMINI_URL = "https://api.llm.stanford.edu"


class LLMProvider(str, Enum):
    NONE = "none"
    GOOGLE_DIRECT = "google_direct"
    STANFORD_LLM = "stanford_llm"  # api.llm.stanford.edu — Gemini REST format
    UIT_GATEWAY = "uit_gateway"  # aiapi-prod — OpenAI-compatible


def get_provider() -> LLMProvider:
    key = settings.gemini_api_key
    if not key:
        return LLMProvider.NONE

    if key.startswith("AIza"):
        return LLMProvider.GOOGLE_DIRECT

    # Explicit Stanford llm.stanford.edu proxy (Gemini REST)
    if settings.google_gemini_base_url:
        return LLMProvider.STANFORD_LLM

    # Explicit UIT OpenAI-compatible gateway
    if settings.llm_base_url and "aiapi-prod" in settings.llm_base_url:
        return LLMProvider.UIT_GATEWAY

    # sk- keys default to llm.stanford.edu (not UIT gateway)
    if key.startswith("sk-"):
        return LLMProvider.STANFORD_LLM

    return LLMProvider.STANFORD_LLM


def is_configured() -> bool:
    return bool(settings.gemini_api_key)


def get_provider_label() -> str:
    return get_provider().value


def chat_completion_text(
    prompt: str,
    *,
    temperature: float = 0.1,
    model: str | None = None,
    thinking_budget: int = 0,
    max_output_tokens: int = 8192,
) -> str:
    """Text-only wrapper over ``chat_completion`` for callers that don't bill."""
    return chat_completion(
        prompt,
        temperature=temperature,
        model=model,
        thinking_budget=thinking_budget,
        max_output_tokens=max_output_tokens,
    ).text


def chat_completion(
    prompt: str,
    *,
    temperature: float = 0.1,
    model: str | None = None,
    thinking_budget: int = 0,
    max_output_tokens: int = 8192,
) -> LLMResult:
    """Route a text prompt to the configured provider.

    `model` overrides the default text model (e.g. a dedicated scoring model).
    `thinking_budget` > 0 enables the model's reasoning pass on the Stanford/Gemini
    REST path (used for scoring); the OpenAI-compatible and google-genai paths reason
    per their own defaults and ignore it.
    """
    provider = get_provider()

    if provider == LLMProvider.STANFORD_LLM:
        from app.services.gemini_rest import generate_text_with_usage

        text, usage = generate_text_with_usage(
            prompt,
            temperature=temperature,
            model=model,
            thinking_budget=thinking_budget,
            max_output_tokens=max_output_tokens,
        )
        return LLMResult(
            text=text,
            input_tokens=_as_int(usage.get("prompt_token_count")),
            # Reasoning tokens bill at the output rate — count them.
            output_tokens=_sum_opt(
                usage.get("candidates_token_count"), usage.get("thoughts_token_count")
            ),
        )

    if provider == LLMProvider.UIT_GATEWAY:
        client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.llm_base_url.rstrip("/") or UIT_GATEWAY_URL,
        )
        response = client.chat.completions.create(
            model=model or settings.gemini_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty response")
        u = getattr(response, "usage", None)
        return LLMResult(
            text=content,
            input_tokens=_as_int(getattr(u, "prompt_tokens", None)),
            output_tokens=_as_int(getattr(u, "completion_tokens", None)),
        )

    if provider == LLMProvider.GOOGLE_DIRECT:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        gen_model = genai.GenerativeModel(model or settings.gemini_model)
        response = gen_model.generate_content(prompt)
        u = getattr(response, "usage_metadata", None)
        return LLMResult(
            text=(response.text or "").strip(),
            input_tokens=_as_int(getattr(u, "prompt_token_count", None)),
            output_tokens=_sum_opt(
                getattr(u, "candidates_token_count", None),
                getattr(u, "thoughts_token_count", None),
            ),
        )

    raise ValueError("No LLM provider configured")


def _as_int(value) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _sum_opt(*values) -> Optional[int]:
    """Sum the reported parts, or None if the provider reported none of them.

    A missing thinking count is 0, not unknown — models without a reasoning pass
    simply omit it, and treating that as "unmetered" would throw away a perfectly
    good candidates count.
    """
    parts = [_as_int(v) for v in values]
    known = [p for p in parts if p is not None]
    return sum(known) if known else None
