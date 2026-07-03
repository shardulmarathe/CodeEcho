"""Audio transcription via Azure Whisper."""

import re
from collections.abc import Callable
from pathlib import Path

from app.config import settings
from app.models import WordTimestamp
from app.services.audio_utils import effective_duration_sec, preprocess_for_transcription
from app.services.budget import check_budget, estimate_whisper_cost, record_cost
from app.services.llm_client import get_provider


def align_transcript_to_timestamps(
    transcript: str, duration_sec: float, *, time_offset: float = 0.0, index_offset: int = 0
) -> list[WordTimestamp]:
    tokens = [t for t in transcript.split() if t.strip()]
    if not tokens:
        return []

    weights = [max(len(re.sub(r"[^\w]", "", t)), 1) for t in tokens]
    total_weight = sum(weights) or 1

    words: list[WordTimestamp] = []
    t = time_offset
    for i, token in enumerate(tokens):
        word_dur = (weights[i] / total_weight) * duration_sec
        words.append(
            WordTimestamp(
                word=token,
                start=round(t, 2),
                end=round(t + word_dur, 2),
                index=index_offset + i,
            )
        )
        t += word_dur

    return words


def _min_words_for_duration(duration_sec: float) -> int:
    if duration_sec < 5:
        return 2
    return max(3, int(duration_sec / 5))


def _apply_live_fallback(
    fallback_transcript: str | None,
    total_duration: float,
    on_partial: Callable[[list[WordTimestamp], str, bool], None] | None,
    audio_name: str,
) -> tuple[list[WordTimestamp], str, float, str] | None:
    fallback = (fallback_transcript or "").strip()
    if fallback and len(fallback.split()) >= 2:
        words = align_transcript_to_timestamps(fallback, total_duration)
        if on_partial:
            on_partial(words, fallback, True)
        record_cost(
            f"{get_provider().value}_transcription",
            f"Live transcript fallback for {audio_name}",
            0.0,
        )
        return words, fallback, total_duration, "live"
    return None


def _transcribe_via_whisper(
    processed_path: Path,
    total_duration: float,
    on_partial: Callable[[list[WordTimestamp], str, bool], None] | None,
    fallback_transcript: str | None,
    audio_name: str,
) -> tuple[list[WordTimestamp], str, float, str]:
    from app.services import whisper

    words, transcript = whisper.transcribe_words(processed_path)
    transcript = transcript.strip()
    word_count = len(transcript.split())
    min_words = _min_words_for_duration(total_duration)

    if not transcript or word_count < min_words:
        live_result = _apply_live_fallback(
            fallback_transcript, total_duration, on_partial, audio_name
        )
        if live_result:
            return live_result
        raise ValueError(
            f"Transcription too short: Whisper returned {word_count} word(s) "
            f"({transcript!r}) for {total_duration:.1f}s of audio "
            f"(need at least {min_words})."
        )

    if not words:
        words = align_transcript_to_timestamps(transcript, total_duration)

    if on_partial:
        on_partial(words, transcript, True)

    record_cost(
        "azure_whisper_transcription",
        f"Whisper transcribe {audio_name}",
        estimate_whisper_cost(total_duration),
    )

    return words, transcript, total_duration, "whisper"


def transcribe_audio(
    audio_path: Path,
    on_partial: Callable[[list[WordTimestamp], str, bool], None] | None = None,
    fallback_transcript: str | None = None,
) -> tuple[list[WordTimestamp], str, float, str]:
    """Returns (words, transcript, duration_sec, source) where source is 'whisper' or 'live'."""
    if not settings.whisper_configured:
        raise ValueError(
            "Whisper is not configured. Set AZURE_OPENAI_WHISPER_DEPLOYMENT "
            "(plus Azure endpoint/key) in backend/.env."
        )

    if audio_path.stat().st_size < 100:
        raise ValueError("Audio file is empty or too short to transcribe")

    check_budget()

    processed_path, temp_path = preprocess_for_transcription(audio_path)
    total_duration = effective_duration_sec(processed_path)

    try:
        return _transcribe_via_whisper(
            processed_path,
            total_duration,
            on_partial,
            fallback_transcript,
            audio_path.name,
        )
    except Exception as exc:
        live_result = _apply_live_fallback(
            fallback_transcript, total_duration, on_partial, audio_path.name
        )
        if live_result:
            return live_result
        raise exc
    finally:
        if temp_path and temp_path.exists():
            import shutil

            shutil.rmtree(temp_path, ignore_errors=True)


def transcribe_audio_mock(audio_path: Path) -> tuple[list[WordTimestamp], str, float]:
    duration = effective_duration_sec(audio_path, words_end=8.0)
    mock_words = [
        WordTimestamp(word="So", start=0.0, end=0.3, index=0),
        WordTimestamp(word="um", start=0.5, end=0.8, index=1),
        WordTimestamp(word="I", start=1.0, end=1.1, index=2),
        WordTimestamp(word="think", start=1.2, end=1.5, index=3),
        WordTimestamp(word="the", start=1.6, end=1.7, index=4),
        WordTimestamp(word="key", start=1.8, end=2.0, index=5),
        WordTimestamp(word="point", start=2.1, end=2.4, index=6),
        WordTimestamp(word="is", start=2.5, end=2.7, index=7),
        WordTimestamp(word="like", start=3.5, end=3.8, index=8),
        WordTimestamp(word="we", start=3.9, end=4.0, index=9),
        WordTimestamp(word="need", start=4.1, end=4.3, index=10),
        WordTimestamp(word="to", start=4.4, end=4.5, index=11),
        WordTimestamp(word="focus.", start=6.1, end=6.6, index=12),
    ]
    transcript = " ".join(w.word for w in mock_words)
    return mock_words, transcript, duration
