"""Debug routes for verifying LLM API connectivity (local dev)."""

import shutil
import tempfile
import time
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import settings
from app.services.budget import record_cost
from app.services.llm_client import (
    chat_completion_text,
    get_provider,
    get_provider_label,
    is_configured,
)
from app.services.transcribe import transcribe_audio

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
async def whisper_audio_test(file: UploadFile = File(...)):
    """Run the production Whisper transcribe_audio() path."""
    if not settings.whisper_configured:
        raise HTTPException(
            status_code=503,
            detail="Whisper is not configured (AZURE_OPENAI_WHISPER_DEPLOYMENT)",
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

        try:
            words, transcript, duration, source = transcribe_audio(raw_path)
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": bool(transcript),
                "provider": "whisper",
                "model": settings.azure_openai_whisper_deployment,
                "latency_ms": latency_ms,
                "audio_duration_sec": round(duration, 2),
                "transcript": transcript,
                "word_count": len(words),
                "transcript_source": source,
                "error": None,
            }
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": False,
                "provider": "whisper",
                "model": settings.azure_openai_whisper_deployment,
                "latency_ms": latency_ms,
                "transcript": None,
                "transcript_source": None,
                "error": str(e),
            }


@router.post("/transcribe-session")
async def transcribe_session_test(
    file: UploadFile = File(...),
    live_transcript: str = Form(""),
):
    """Run the exact transcribe_audio() path used by the main app."""
    if not settings.whisper_configured:
        raise HTTPException(
            status_code=503,
            detail="Whisper is not configured (AZURE_OPENAI_WHISPER_DEPLOYMENT)",
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
