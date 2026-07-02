"""Unified LLM client — routes to the correct provider."""

from enum import Enum
from pathlib import Path

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


def chat_completion_text(prompt: str, *, temperature: float = 0.1) -> str:
    """Route a text prompt to the configured provider."""
    provider = get_provider()

    if provider == LLMProvider.STANFORD_LLM:
        from app.services.gemini_rest import generate_text

        return generate_text(prompt, temperature=temperature)

    if provider == LLMProvider.UIT_GATEWAY:
        client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.llm_base_url.rstrip("/") or UIT_GATEWAY_URL,
        )
        response = client.chat.completions.create(
            model=settings.gemini_model,
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
        model = genai.GenerativeModel(settings.gemini_model)
        response = model.generate_content(prompt)
        return (response.text or "").strip()

    raise ValueError("No LLM provider configured")


def chat_with_audio_file(
    audio_path: Path, *, temperature: float = 0.0, with_text_cue: bool = False
) -> str:
    """Route audio transcription to the configured provider."""
    provider = get_provider()

    if provider == LLMProvider.STANFORD_LLM:
        from app.services.gemini_rest import (
            generate_with_audio_and_cue,
            transcribe_audio_file as stanford_transcribe,
        )

        if with_text_cue:
            return generate_with_audio_and_cue(audio_path, temperature=temperature)
        return stanford_transcribe(audio_path, temperature=temperature).text

    transcription_prompt = (
        "Transcribe the audio verbatim. Output only the spoken words."
    )

    if provider == LLMProvider.UIT_GATEWAY:
        import base64

        mime = _mime_type(audio_path)
        audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")
        client = OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.llm_base_url.rstrip("/") or UIT_GATEWAY_URL,
        )
        response = client.chat.completions.create(
            model=settings.effective_transcription_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{audio_b64}"},
                        },
                        {"type": "text", "text": transcription_prompt},
                    ],
                }
            ],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty response")
        return content

    if provider == LLMProvider.GOOGLE_DIRECT:
        return _google_direct_audio(audio_path, transcription_prompt, temperature)

    raise ValueError("No LLM provider configured")


def _google_direct_audio(audio_path: Path, prompt: str, temperature: float) -> str:
    import time

    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.effective_transcription_model)
    uploaded = genai.upload_file(path=str(audio_path), mime_type=_mime_type(audio_path))

    deadline = time.time() + 120
    file_ref = uploaded
    while file_ref.state.name == "PROCESSING":
        if time.time() > deadline:
            raise TimeoutError("Gemini audio file processing timed out")
        time.sleep(1)
        file_ref = genai.get_file(file_ref.name)

    response = model.generate_content(
        [uploaded, prompt],
        generation_config=genai.GenerationConfig(temperature=temperature),
    )
    try:
        genai.delete_file(uploaded.name)
    except Exception:
        pass
    return (response.text or "").strip()


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


def transcribe_with_strategies(
    audio_path: Path,
    *,
    temperature: float = 0.0,
    min_words: int = 1,
):
    """Transcribe audio with provider-specific strategy ladder and metadata."""
    from app.services.gemini_rest import TranscriptionResult

    provider = get_provider()

    if provider == LLMProvider.STANFORD_LLM:
        from app.services.gemini_rest import transcribe_audio_file as stanford_transcribe

        return stanford_transcribe(
            audio_path, temperature=temperature, min_words=min_words
        )

    if provider == LLMProvider.GOOGLE_DIRECT:
        text = _google_direct_audio(
            audio_path,
            "Transcribe the audio verbatim. Output only the spoken words.",
            temperature,
        )
        return TranscriptionResult(
            text=text,
            strategy="google_direct_files_api",
            model=settings.effective_transcription_model,
        )

    if provider == LLMProvider.UIT_GATEWAY:
        text = chat_with_audio_file(audio_path, temperature=temperature)
        return TranscriptionResult(
            text=text,
            strategy="uit_gateway",
            model=settings.effective_transcription_model,
        )

    raise ValueError("No LLM provider configured")
