"""Unified LLM client — routes to the correct provider."""

from enum import Enum

from openai import OpenAI

from app.config import settings

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
    """Route a text prompt to the configured provider.

    `model` overrides the default text model (e.g. a dedicated scoring model).
    `thinking_budget` > 0 enables the model's reasoning pass on the Stanford/Gemini
    REST path (used for scoring); the OpenAI-compatible and google-genai paths reason
    per their own defaults and ignore it.
    """
    provider = get_provider()

    if provider == LLMProvider.STANFORD_LLM:
        from app.services.gemini_rest import generate_text

        return generate_text(
            prompt,
            temperature=temperature,
            model=model,
            thinking_budget=thinking_budget,
            max_output_tokens=max_output_tokens,
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
        return content

    if provider == LLMProvider.GOOGLE_DIRECT:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        gen_model = genai.GenerativeModel(model or settings.gemini_model)
        response = gen_model.generate_content(prompt)
        return (response.text or "").strip()

    raise ValueError("No LLM provider configured")
