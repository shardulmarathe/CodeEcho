"""Debug routes for verifying LLM API connectivity (local dev)."""

import shutil
import tempfile
import time
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import settings
from app.services.audio_utils import (
    effective_duration_sec,
    preprocess_for_transcription,
    split_audio_into_chunks,
)
from app.services.budget import record_cost
from app.services.llm_client import (
    chat_completion_text,
    get_provider,
    get_provider_label,
    is_configured,
    transcribe_with_strategies,
)
from app.services.transcribe import (
    CHUNK_DURATION_SEC,
    MIN_DURATION_TO_CHUNK_SEC,
    TranscriptFailureReason,
    _clean_verbatim,
    classify_transcript_failure,
    transcribe_audio,
)

router = APIRouter(prefix="/debug/gemini", tags=["debug"])

PING_PROMPT = "Reply with exactly: OK"
ANALYSIS_PROMPT = """Analyze this speech transcript for filler words and speech clarity.
Transcript:
{text}

Return:
1. Filler words found (with counts)
2. Brief 2-3 sentence assessment
3. One concrete improvement tip"""


class TextTestRequest(BaseModel):
    text: str = Field(..., min_length=5)


def _base_url() -> str | None:
    if settings.google_gemini_base_url:
        return settings.google_gemini_base_url.rstrip("/")
    if settings.llm_base_url:
        return settings.llm_base_url.rstrip("/")
    return None


def _audio_diagnostic_result(
    *,
    ok: bool,
    latency_ms: int,
    duration: float,
    audio_bytes: int,
    raw_response: str | None,
    cleaned_transcript: str | None,
    failure_reason: str | None,
    chunk_count: int,
    transcript_source: str | None = None,
    strategy: str | None = None,
    model: str | None = None,
    usage: dict | None = None,
    attempts: list | None = None,
    error: str | None = None,
) -> dict:
    return {
        "ok": ok,
        "provider": get_provider_label(),
        "model": model or settings.effective_transcription_model,
        "base_url": _base_url(),
        "latency_ms": latency_ms,
        "audio_duration_sec": round(duration, 2),
        "audio_bytes": audio_bytes,
        "chunk_count": chunk_count,
        "raw_response": raw_response,
        "cleaned_transcript": cleaned_transcript,
        "transcript": cleaned_transcript,
        "failure_reason": failure_reason,
        "transcript_source": transcript_source,
        "strategy": strategy,
        "usage": usage,
        "attempts": attempts,
        "likely_hallucination": failure_reason == TranscriptFailureReason.HALLUCINATION.value,
        "error": error,
    }


@router.get("/ping")
async def gemini_ping():
    if not is_configured():
        return {
            "ok": False,
            "provider": get_provider_label(),
            "model": settings.gemini_model,
            "base_url": _base_url(),
            "latency_ms": 0,
            "response": None,
            "error": "GEMINI_API_KEY is not configured in backend/.env",
        }

    start = time.perf_counter()
    try:
        response = chat_completion_text(PING_PROMPT, temperature=0.0)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "provider": get_provider_label(),
            "model": settings.gemini_model,
            "base_url": _base_url(),
            "latency_ms": latency_ms,
            "response": response.strip(),
            "error": None,
        }
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": False,
            "provider": get_provider_label(),
            "model": settings.gemini_model,
            "base_url": _base_url(),
            "latency_ms": latency_ms,
            "response": None,
            "error": str(e),
        }


@router.post("/text")
async def gemini_text_test(body: TextTestRequest):
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured in backend/.env",
        )

    prompt = ANALYSIS_PROMPT.format(text=body.text.strip())
    start = time.perf_counter()

    try:
        analysis = chat_completion_text(prompt, temperature=0.2)
        latency_ms = int((time.perf_counter() - start) * 1000)
        record_cost(
            f"{get_provider().value}_debug",
            "Gemini text smoke test",
            0.0001,
        )
        return {
            "ok": True,
            "provider": get_provider_label(),
            "model": settings.gemini_model,
            "base_url": _base_url(),
            "latency_ms": latency_ms,
            "input_text": body.text.strip(),
            "analysis": analysis.strip(),
            "error": None,
        }
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": False,
            "provider": get_provider_label(),
            "model": settings.gemini_model,
            "base_url": _base_url(),
            "latency_ms": latency_ms,
            "input_text": body.text.strip(),
            "analysis": None,
            "error": str(e),
        }


@router.post("/audio")
async def gemini_audio_test(file: UploadFile = File(...)):
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured in backend/.env",
        )
    if not shutil.which("ffmpeg"):
        raise HTTPException(
            status_code=503,
            detail="ffmpeg is not installed. Run: brew install ffmpeg",
        )

    suffix = Path(file.filename or "audio.webm").suffix.lower() or ".webm"
    start = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="codeecho_debug_audio_") as tmp:
        raw_path = Path(tmp) / f"upload{suffix}"
        raw_path.write_bytes(await file.read())
        wav_path, wav_tmp = preprocess_for_transcription(raw_path)
        duration = effective_duration_sec(wav_path)
        audio_bytes = wav_path.stat().st_size
        chunk_specs, _ = split_audio_into_chunks(
            wav_path,
            CHUNK_DURATION_SEC,
            min_duration_to_chunk=MIN_DURATION_TO_CHUNK_SEC,
        )

        try:
            result = transcribe_with_strategies(wav_path, temperature=0.0, min_words=1)
            raw = result.text
            cleaned = _clean_verbatim(raw)
            latency_ms = int((time.perf_counter() - start) * 1000)
            reason = classify_transcript_failure(raw, cleaned, duration)
            failure = reason.value if reason else None
            record_cost(
                f"{get_provider().value}_debug",
                "Gemini audio smoke test",
                0.0005,
            )
            attempts = [
                {
                    "strategy": a.strategy,
                    "model": a.model,
                    "ok": a.ok,
                    "latency_ms": a.latency_ms,
                    "error": a.error,
                    "finish_reason": a.finish_reason,
                    "usage": a.usage,
                }
                for a in result.attempts
            ]
            return _audio_diagnostic_result(
                ok=bool(cleaned) and reason is None,
                latency_ms=latency_ms,
                duration=duration,
                audio_bytes=audio_bytes,
                raw_response=raw,
                cleaned_transcript=cleaned or None,
                failure_reason=failure,
                chunk_count=len(chunk_specs),
                strategy=result.strategy,
                model=result.model,
                usage=result.usage,
                attempts=attempts,
                error=None
                if reason is None
                else f"Transcription issue: {failure}",
            )
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return _audio_diagnostic_result(
                ok=False,
                latency_ms=latency_ms,
                duration=duration,
                audio_bytes=audio_bytes,
                raw_response=None,
                cleaned_transcript=None,
                failure_reason=TranscriptFailureReason.API_ERROR.value,
                chunk_count=len(chunk_specs),
                error=str(e),
            )
        finally:
            if wav_tmp and wav_tmp.exists():
                shutil.rmtree(wav_tmp, ignore_errors=True)


@router.post("/transcribe-session")
async def gemini_transcribe_session_test(
    file: UploadFile = File(...),
    live_transcript: str = Form(""),
):
    """Run the exact transcribe_audio() path used by the main app."""
    from app.config import settings as app_settings

    if not app_settings.transcription_configured:
        raise HTTPException(
            status_code=503,
            detail="No transcription provider configured (Whisper or GEMINI_API_KEY)",
        )
    if not shutil.which("ffmpeg"):
        raise HTTPException(status_code=503, detail="ffmpeg not installed")

    suffix = Path(file.filename or "audio.webm").suffix.lower() or ".webm"
    start = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="codeecho_debug_session_") as tmp:
        raw_path = Path(tmp) / f"upload{suffix}"
        raw_path.write_bytes(await file.read())

        try:
            words, transcript, duration, source = transcribe_audio(
                raw_path,
                fallback_transcript=live_transcript.strip() or None,
            )
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": True,
                "latency_ms": latency_ms,
                "audio_duration_sec": round(duration, 2),
                "transcript": transcript,
                "word_count": len(words),
                "transcript_source": source,
                "live_fallback_available": bool(live_transcript.strip()),
                "used_live_fallback": source == "live",
                "error": None,
            }
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": False,
                "latency_ms": latency_ms,
                "transcript": None,
                "transcript_source": None,
                "live_fallback_available": bool(live_transcript.strip()),
                "used_live_fallback": False,
                "error": str(e),
            }
