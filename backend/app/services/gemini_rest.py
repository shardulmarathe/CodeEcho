"""Google Gemini REST API client (works with Stanford api.llm.stanford.edu proxy)."""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import httpx

from app.config import settings

STANFORD_LLM_GEMINI_URL = "https://api.llm.stanford.edu"

TRANSCRIPTION_PROMPT = (
    "Generate a transcript of the speech in this audio. "
    "Output only the spoken words verbatim, including filler words like um and uh. "
    "Transcribe once — do not loop or repeat words."
)

MINIMAL_CUE = "Output the transcript of this audio:"


@dataclass
class TranscriptionAttempt:
    strategy: str
    model: str
    ok: bool
    text: str = ""
    error: str | None = None
    latency_ms: int = 0
    finish_reason: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscriptionResult:
    text: str
    strategy: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    attempts: list[TranscriptionAttempt] = field(default_factory=list)


def _base_url() -> str:
    url = settings.google_gemini_base_url or STANFORD_LLM_GEMINI_URL
    return url.rstrip("/")


def _auth_headers(extra: dict | None = None) -> dict:
    """Auth via header, never the URL.

    Putting the API key in the query string (``?key=...``) leaks it into proxy/server
    access logs and into any error that stringifies the request URL. The Gemini REST
    API (and the Stanford proxy) accept the key in the ``x-goog-api-key`` header.
    """
    headers = {"x-goog-api-key": settings.gemini_api_key}
    if extra:
        headers.update(extra)
    return headers


def _model_path(model_name: str) -> str:
    model = model_name
    if not model.startswith("models/"):
        model = f"models/{model}"
    return model


def generate_text(prompt: str, *, temperature: float = 0.1) -> str:
    """Text-only generateContent call."""
    text, _ = _generate_content(
        parts=[{"text": prompt}],
        temperature=temperature,
        model=settings.gemini_model,
    )
    return text


def transcribe_audio_file(
    audio_path: Path,
    *,
    temperature: float = 0.0,
    min_words: int = 1,
) -> TranscriptionResult:
    """
    Try multiple Gemini request strategies until one returns usable speech text.
    """
    attempts: list[TranscriptionAttempt] = []
    primary_model = settings.effective_transcription_model
    flash_model = settings.gemini_model.strip() or "gemini-2.5-flash"

    # Flash first — Stanford proxy returns 400 for thinkingBudget on pro, and pro
    # often returns empty text when thinking consumes the output budget.
    strategies: list[tuple[str, str, Callable[[Path], list[dict]]]] = [
        ("text_plus_inline_flash", flash_model, _parts_text_plus_inline),
        ("text_plus_inline_audio", primary_model, _parts_text_plus_inline),
        ("files_api", flash_model, _parts_files_api),
    ]

    for strategy_name, model, parts_builder in strategies:
        attempt = _run_strategy(
            audio_path,
            strategy_name=strategy_name,
            model=model,
            parts_builder=parts_builder,
            temperature=temperature,
        )
        attempts.append(attempt)
        if attempt.ok and len(attempt.text.split()) >= min_words:
            return TranscriptionResult(
                text=attempt.text,
                strategy=strategy_name,
                model=model,
                usage=attempt.usage,
                attempts=attempts,
            )

    errors = "; ".join(
        f"{a.strategy} ({a.model}): {(a.error or 'empty')[:200]}" for a in attempts if not a.ok
    )
    raise ValueError(
        f"All Gemini transcription strategies failed for {audio_path.name}. "
        f"Tried: {', '.join(a.strategy for a in attempts)}. {errors}"
    )


def generate_with_audio(audio_path: Path, *, temperature: float = 0.0) -> str:
    """Backward-compatible single-strategy transcription."""
    return transcribe_audio_file(audio_path, temperature=temperature).text


def generate_with_audio_and_cue(
    audio_path: Path, *, temperature: float = 0.0
) -> str:
    """Backward-compatible cue retry path."""
    attempt = _run_strategy(
        audio_path,
        strategy_name="minimal_cue_inline",
        model=settings.effective_transcription_model,
        parts_builder=_parts_minimal_cue,
        temperature=temperature,
    )
    if attempt.ok:
        return attempt.text
    raise ValueError(attempt.error or "Transcription failed")


def _parts_text_plus_inline(audio_path: Path) -> list[dict]:
    mime = _mime_type(audio_path)
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")
    return [
        {"inline_data": {"mime_type": mime, "data": audio_b64}},
        {"text": TRANSCRIPTION_PROMPT},
    ]


def _parts_minimal_cue(audio_path: Path) -> list[dict]:
    mime = _mime_type(audio_path)
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")
    return [
        {"inline_data": {"mime_type": mime, "data": audio_b64}},
        {"text": MINIMAL_CUE},
    ]


def _parts_files_api(audio_path: Path) -> list[dict]:
    file_uri = _upload_file(audio_path)
    return [
        {"text": TRANSCRIPTION_PROMPT},
        {"file_data": {"mime_type": _mime_type(audio_path), "file_uri": file_uri}},
    ]


def _upload_file(audio_path: Path) -> str:
    """Upload audio via Gemini Files API and return file URI."""
    mime = _mime_type(audio_path)
    upload_url = f"{_base_url()}/upload/v1beta/files"

    with httpx.Client(timeout=180.0) as client:
        response = client.post(
            upload_url,
            headers=_auth_headers({"X-Goog-Upload-Protocol": "multipart"}),
            files={
                "metadata": (
                    None,
                    json.dumps({"file": {"displayName": audio_path.name}}),
                    "application/json",
                ),
                "file": (audio_path.name, audio_path.read_bytes(), mime),
            },
        )
        if response.status_code >= 400:
            raise ValueError(
                f"Files API upload failed {response.status_code}: {response.text[:300]}"
            )
        data = response.json()
        file_info = data.get("file") or data
        file_uri = file_info.get("uri") or file_info.get("name")
        if not file_uri:
            raise ValueError(
                f"Files API returned no URI. Response: {json.dumps(data)[:300]}"
            )

        state = file_info.get("state", "ACTIVE")
        file_name = file_info.get("name", file_uri)
        deadline = time.time() + 120
        while state == "PROCESSING":
            if time.time() > deadline:
                raise TimeoutError("Gemini file processing timed out")
            time.sleep(1)
            status = client.get(
                f"{_base_url()}/v1beta/{file_name}",
                headers=_auth_headers(),
            )
            if status.status_code >= 400:
                break
            file_info = status.json()
            state = file_info.get("state", "ACTIVE")

        return file_uri


def _run_strategy(
    audio_path: Path,
    *,
    strategy_name: str,
    model: str,
    parts_builder,
    temperature: float,
) -> TranscriptionAttempt:
    start = time.perf_counter()
    try:
        parts = parts_builder(audio_path)
        text, usage = _generate_content(
            parts=parts,
            temperature=temperature,
            model=model,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        if not text.strip():
            return TranscriptionAttempt(
                strategy=strategy_name,
                model=model,
                ok=False,
                error="empty text",
                latency_ms=latency_ms,
                usage=usage,
            )
        return TranscriptionAttempt(
            strategy=strategy_name,
            model=model,
            ok=True,
            text=text,
            latency_ms=latency_ms,
            finish_reason=usage.get("finish_reason"),
            usage=usage,
        )
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return TranscriptionAttempt(
            strategy=strategy_name,
            model=model,
            ok=False,
            error=str(e),
            latency_ms=latency_ms,
        )


def _extract_text_from_response(data: dict) -> tuple[str, dict[str, Any]]:
    prompt_feedback = data.get("promptFeedback") or {}
    block_reason = prompt_feedback.get("blockReason")
    if block_reason:
        raise ValueError(
            f"Gemini blocked the request (blockReason={block_reason}). "
            f"Response: {json.dumps(data)[:300]}"
        )

    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError(
            f"Gemini returned no candidates. Response: {json.dumps(data)[:300]}"
        )

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "UNKNOWN")
    if finish_reason in ("SAFETY", "RECITATION", "BLOCKLIST"):
        raise ValueError(
            f"Gemini blocked transcription (finishReason={finish_reason}). "
            f"Response: {json.dumps(data)[:300]}"
        )

    content = candidate.get("content") or {}
    parts = content.get("parts") or []
    texts: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        if part.get("thought"):
            continue
        if part.get("text"):
            texts.append(part["text"])

    usage_meta = data.get("usageMetadata") or {}
    usage = {
        "prompt_token_count": usage_meta.get("promptTokenCount"),
        "candidates_token_count": usage_meta.get("candidatesTokenCount"),
        "thoughts_token_count": usage_meta.get("thoughtsTokenCount"),
        "total_token_count": usage_meta.get("totalTokenCount"),
        "finish_reason": finish_reason,
        "prompt_tokens_details": usage_meta.get("promptTokensDetails"),
    }

    if not texts:
        raise ValueError(
            f"Gemini returned empty text (finishReason={finish_reason}). "
            f"usage={json.dumps(usage)[:200]}. "
            f"Response: {json.dumps(data)[:300]}"
        )

    return "".join(texts).strip(), usage


def _generation_config(temperature: float) -> dict:
    # thinkingBudget=0 disables the model's hidden "thinking" pass, which otherwise
    # dominates latency (~5s -> ~1s per call) and isn't needed for our generation /
    # classification / transcription tasks. If a model/endpoint rejects it,
    # _generate_content falls back to a minimal config (see below).
    return {
        "temperature": temperature,
        "maxOutputTokens": 8192,
        "thinkingConfig": {"thinkingBudget": 0},
    }


def _generate_content(
    parts: list[dict],
    *,
    temperature: float,
    model: str,
    system_instruction: str | None = None,
) -> tuple[str, dict[str, Any]]:
    model_path = _model_path(model)
    url = f"{_base_url()}/v1beta/{model_path}:generateContent"
    headers = _auth_headers()
    payload: dict = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": _generation_config(temperature),
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    minimal_config = {"temperature": temperature}
    with httpx.Client(timeout=180.0) as client:
        response = client.post(url, headers=headers, json=payload)
        # The proxy may reject parts of generationConfig (thinkingConfig / maxOutputTokens
        # support varies by model). On a 400, retry once with a minimal config before failing.
        if response.status_code == 400 and payload["generationConfig"] != minimal_config:
            payload["generationConfig"] = minimal_config
            response = client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise ValueError(
                f"Gemini API error {response.status_code} from {_base_url()}: {response.text[:500]}"
            )
        data = response.json()

    return _extract_text_from_response(data)


def _mime_type(path: Path) -> str:
    mapping = {
        ".webm": "audio/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".mp4": "audio/mp4",
    }
    return mapping.get(path.suffix.lower(), "audio/webm")
