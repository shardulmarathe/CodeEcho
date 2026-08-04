"""Azure OpenAI Whisper transcription with native word-level timestamps.

Unlike the Gemini REST path (which returns plain text that we then align to
timings by character weight), Whisper's ``verbose_json`` response format with
``timestamp_granularities[]=word`` returns real per-word start/end times — so we
build ``WordTimestamp`` objects directly, which is what the filler/pause tracker
needs. Answer scoring still runs on Gemini via ``llm_client``; this module only
does speech-to-text.

Enabled when ``settings.whisper_configured`` (Azure Whisper deployment + creds).
"""

from __future__ import annotations

from pathlib import Path

import httpx

from app.config import settings
from app.models import WordTimestamp

# Biases Whisper toward transcribing disfluencies verbatim rather than cleaning
# them up, filler words are the whole point of this app.
WHISPER_PROMPT = "Transcribe verbatim, including filler words like um, uh, like, and you know."


def _mime_type(path: Path) -> str:
    mapping = {
        ".webm": "audio/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".mp4": "audio/mp4",
    }
    return mapping.get(path.suffix.lower(), "audio/wav")


def transcribe_words(audio_path: Path, *, temperature: float = 0.0) -> tuple[list[WordTimestamp], str]:
    """Transcribe ``audio_path`` via Azure Whisper.

    Returns ``(words, transcript)``. ``words`` carries real word-level timestamps
    when the API returns them; it may be empty (older api-versions omit word
    granularity), in which case the caller aligns ``transcript`` to timings.
    """
    base = settings.whisper_endpoint
    deployment = settings.azure_openai_whisper_deployment
    url = (
        f"{base}/openai/deployments/{deployment}/audio/transcriptions"
        f"?api-version={settings.azure_openai_whisper_api_version}"
    )
    headers = {"api-key": settings.whisper_api_key}
    data = {
        "response_format": "verbose_json",
        "timestamp_granularities[]": "word",
        "temperature": str(temperature),
        "prompt": WHISPER_PROMPT,
        # Pin English, interview answers are English, and a hint avoids Whisper
        # occasionally misdetecting the language on short or accented clips.
        "language": "en",
    }

    with httpx.Client(timeout=180.0) as client:
        with audio_path.open("rb") as fh:
            files = {"file": (audio_path.name, fh, _mime_type(audio_path))}
            resp = client.post(url, headers=headers, data=data, files=files)

    if resp.status_code >= 400:
        # Surface a short, key-free error (the api-key lives in a header, not the URL).
        detail = resp.text[:200] if resp.text else resp.reason_phrase
        raise ValueError(f"Whisper transcription failed ({resp.status_code}): {detail}")

    payload = resp.json()
    transcript = (payload.get("text") or "").strip()

    words: list[WordTimestamp] = []
    for entry in payload.get("words") or []:
        token = (entry.get("word") or "").strip()
        if not token:
            continue
        try:
            start = float(entry.get("start", 0.0))
            end = float(entry.get("end", start))
        except (TypeError, ValueError):
            continue
        words.append(
            WordTimestamp(
                word=token,
                start=round(start, 2),
                end=round(max(end, start), 2),
                index=len(words),
            )
        )

    return words, transcript
