"""Google Gemini REST API client (works with Stanford api.llm.stanford.edu proxy)."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings

STANFORD_LLM_GEMINI_URL = "https://api.llm.stanford.edu"


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


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.1,
    model: str | None = None,
    thinking_budget: int = 0,
    max_output_tokens: int = 8192,
) -> str:
    """Text-only generateContent call.

    `thinking_budget` > 0 lets the model reason before answering (used by scoring);
    the default 0 keeps the fast, no-thinking behavior for fillers/transitions.
    """
    text, _ = _generate_content(
        parts=[{"text": prompt}],
        temperature=temperature,
        model=model or settings.gemini_model,
        thinking_budget=thinking_budget,
        max_output_tokens=max_output_tokens,
    )
    return text


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


def _generation_config(
    temperature: float,
    *,
    thinking_budget: int = 0,
    max_output_tokens: int = 8192,
) -> dict:
    # thinkingBudget=0 disables the model's hidden "thinking" pass, which otherwise
    # dominates latency (~5s -> ~1s per call) and isn't needed for our generation /
    # classification tasks. Scoring passes a positive budget so the model actually
    # reasons about the rubric. A negative budget omits thinkingConfig entirely (use
    # the model's own default). If a model/endpoint rejects the config,
    # _generate_content falls back to a minimal config (see below).
    config: dict = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    if thinking_budget >= 0:
        config["thinkingConfig"] = {"thinkingBudget": thinking_budget}
    return config


def _generate_content(
    parts: list[dict],
    *,
    temperature: float,
    model: str,
    system_instruction: str | None = None,
    thinking_budget: int = 0,
    max_output_tokens: int = 8192,
) -> tuple[str, dict[str, Any]]:
    model_path = _model_path(model)
    url = f"{_base_url()}/v1beta/{model_path}:generateContent"
    headers = _auth_headers()
    payload: dict = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": _generation_config(
            temperature,
            thinking_budget=thinking_budget,
            max_output_tokens=max_output_tokens,
        ),
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
