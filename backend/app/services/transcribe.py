"""Audio transcription via configured LLM provider."""

import re
from collections.abc import Callable
from enum import Enum
from pathlib import Path
import shutil

from app.config import settings
from app.models import WordTimestamp
from app.services.audio_utils import (
    effective_duration_sec,
    preprocess_for_transcription,
    split_audio_into_chunks,
)
from app.services.budget import (
    check_budget,
    estimate_gemini_audio_cost,
    estimate_whisper_cost,
    record_cost,
)
from app.services.llm_client import get_provider, is_configured, transcribe_with_strategies

CHUNK_DURATION_SEC = 15.0
MIN_DURATION_TO_CHUNK_SEC = 30.0

PROMPT_ECHO_PHRASES = (
    "transcribe the spoken words in this audio",
    "transcribe the attached audio verbatim",
    "transcribe the audio verbatim",
    "generate a transcript of the speech",
    "output only the transcript",
    "output only the spoken words",
    "output the transcript of this audio",
    "no commentary, labels, or explanation",
    "include filler words",
    "do not add labels, commentary",
    "transcribe:",
)

REFUSAL_RE = re.compile(
    r"("
    r"i(?:'m| am) not sure if i(?:'m| am) going to be able to get the whole"
    r"|i(?:'m| am) not sure if i can transcribe"
    r"|i(?:'m| am) not sure how to transcribe"
    r"|i(?:'m| am) unable to (?:transcribe|listen|hear|process)"
    r"|i cannot transcribe|i can't transcribe"
    r"|unable to transcribe|cannot transcribe"
    r"|don't have access to (?:the )?audio"
    r"|whole thing in one go"
    r"|as an ai language model"
    r")",
    re.IGNORECASE,
)

MODEL_HALLUCINATION_RE = re.compile(
    r"^i(?:'m| am) not sure if i(?:'m| am) going to be able to\b",
    re.IGNORECASE,
)


class TranscriptFailureReason(str, Enum):
    EMPTY_RESPONSE = "empty_response"
    PROMPT_ECHO_ONLY = "prompt_echo_only"
    HALLUCINATION = "hallucination"
    API_ERROR = "api_error"


def _strip_prompt_echo(text: str) -> str:
    """Remove echoed instruction text only when real speech follows."""
    original = text.strip()
    if not original:
        return ""

    lowered = original.lower()
    if not any(phrase in lowered for phrase in PROMPT_ECHO_PHRASES):
        return original

    cleaned = original
    for phrase in PROMPT_ECHO_PHRASES:
        if phrase in lowered:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            cleaned = pattern.sub("", cleaned)

    cleaned = re.sub(r"^[\s.:,;]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Keep original if stripping removed everything but original had extra words
    if not cleaned and len(original.split()) > len(PROMPT_ECHO_PHRASES):
        return original
    return cleaned or original


def _clean_verbatim(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    text = re.sub(r"^(transcript|transcription):\s*", "", text, flags=re.IGNORECASE)
    text = _strip_prompt_echo(text)
    return text.strip().strip('"')


def _normalize_token(word: str) -> str:
    return re.sub(r"[^\w']", "", word.lower())


def _collapse_runaway_repetition(text: str, duration_sec: float) -> str:
    """
    Gemini sometimes loops one word thousands of times on repetitive speech.
    Cap consecutive duplicates and total length to a plausible upper bound.
    """
    words = text.split()
    if not words:
        return text

    # ~4.5 words/sec is very fast speech; generous ceiling for short clips.
    max_total = max(12, int(duration_sec * 4.5))
    max_consecutive = max(4, min(24, int(duration_sec * 0.8) + 2))

    collapsed: list[str] = []
    i = 0
    while i < len(words):
        token = _normalize_token(words[i])
        run = 1
        while (
            i + run < len(words)
            and _normalize_token(words[i + run]) == token
        ):
            run += 1
        take = min(run, max_consecutive)
        collapsed.extend(words[i : i + take])
        i += run

    if len(collapsed) > max_total:
        collapsed = collapsed[:max_total]

    return " ".join(collapsed)


def _clean_transcript(text: str, duration_sec: float) -> str:
    cleaned = _clean_verbatim(text)
    return _collapse_runaway_repetition(cleaned, duration_sec)


def _is_prompt_echo_only(text: str) -> bool:
    cleaned = _strip_prompt_echo(text).strip()
    raw = text.strip()
    if not raw:
        return False
    lowered = raw.lower()
    has_echo = any(phrase in lowered for phrase in PROMPT_ECHO_PHRASES)
    if not has_echo:
        return False
    # Echo only if almost nothing remains after stripping
    return not cleaned or len(cleaned.split()) < 2


def classify_transcript_failure(
    raw: str, cleaned: str, chunk_duration_sec: float
) -> TranscriptFailureReason | None:
    if not raw.strip():
        return TranscriptFailureReason.EMPTY_RESPONSE
    if not cleaned:
        return (
            TranscriptFailureReason.PROMPT_ECHO_ONLY
            if _is_prompt_echo_only(raw)
            else TranscriptFailureReason.EMPTY_RESPONSE
        )
    if _is_prompt_echo_only(raw):
        return TranscriptFailureReason.PROMPT_ECHO_ONLY
    if REFUSAL_RE.search(cleaned) or MODEL_HALLUCINATION_RE.match(cleaned):
        return TranscriptFailureReason.HALLUCINATION
    words = cleaned.split()
    if (
        chunk_duration_sec >= 3
        and len(words) <= 10
        and re.match(r"^i(?:'m| am) not sure\b", cleaned, re.IGNORECASE)
    ):
        return TranscriptFailureReason.HALLUCINATION
    if len(words) < 4 and any(
        w in cleaned.lower() for w in ("sorry", "cannot", "can't", "unable")
    ):
        return TranscriptFailureReason.HALLUCINATION
    return None


def _transcription_error_message(
    raw: str, reason: TranscriptFailureReason, *, audio_duration_sec: float | None = None
) -> str:
    snippet = raw[:200] if raw.strip() else "(empty)"
    duration_note = (
        f" Audio duration: {audio_duration_sec:.1f}s."
        if audio_duration_sec is not None
        else ""
    )
    if reason == TranscriptFailureReason.EMPTY_RESPONSE:
        return (
            "Gemini returned an empty transcription after trying all strategies."
            f"{duration_note} Model returned: {snippet}"
        )
    if reason == TranscriptFailureReason.PROMPT_ECHO_ONLY:
        return (
            "The model echoed instructions instead of transcribing your audio."
            f"{duration_note} Model returned: {snippet}"
        )
    return (
        "The model did not transcribe your audio — it generated a placeholder instead."
        f"{duration_note} Model returned: {snippet}"
    )


def _transcribe_chunk(audio_path: Path, chunk_duration_sec: float) -> str:
    min_words = _min_words_for_duration(chunk_duration_sec)
    try:
        result = transcribe_with_strategies(
            audio_path, temperature=0.0, min_words=min_words
        )
        raw = result.text
    except Exception as e:
        raise ValueError(
            _transcription_error_message(
                str(e),
                TranscriptFailureReason.API_ERROR,
                audio_duration_sec=chunk_duration_sec,
            )
        ) from e

    transcript = _clean_transcript(raw, chunk_duration_sec)
    reason = classify_transcript_failure(raw, transcript, chunk_duration_sec)
    word_count = len(transcript.split()) if transcript else 0

    if transcript and reason is None and word_count >= min_words:
        return transcript

    if transcript and reason is None and word_count < min_words:
        raise ValueError(
            f"Gemini returned too few words for {chunk_duration_sec:.1f}s of audio: "
            f"{transcript!r} (got {word_count}, need {min_words})."
        )

    failure_reason = reason or TranscriptFailureReason.EMPTY_RESPONSE
    raise ValueError(
        _transcription_error_message(
            raw,
            failure_reason,
            audio_duration_sec=chunk_duration_sec,
        )
    )


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
    """Expected minimum word count — catches Gemini returning a single word for long audio."""
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


def _reindex_words(words: list[WordTimestamp]) -> list[WordTimestamp]:
    return [
        WordTimestamp(word=w.word, start=w.start, end=w.end, index=i)
        for i, w in enumerate(words)
    ]


def _transcribe_via_whisper(
    processed_path: Path,
    total_duration: float,
    on_partial: Callable[[list[WordTimestamp], str, bool], None] | None,
    fallback_transcript: str | None,
    audio_name: str,
) -> tuple[list[WordTimestamp], str, float, str]:
    """Transcribe via Azure Whisper (single request, real word-level timestamps).

    Whisper does not loop/refuse/echo the way Gemini does, so it needs none of the
    repetition-collapse or hallucination cleanup the Gemini path carries.
    """
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

    # Fall back to character-weighted timings only if the API omitted word timestamps.
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
    """
    Returns (words, transcript, duration_sec, source) where source is
    'whisper', 'gemini', or 'live'.
    """
    if not settings.transcription_configured:
        raise ValueError(
            "No transcription provider configured. Set AZURE_OPENAI_WHISPER_DEPLOYMENT "
            "(plus Azure endpoint/key) or GEMINI_API_KEY in backend/.env."
        )

    if audio_path.stat().st_size < 100:
        raise ValueError("Audio file is empty or too short to transcribe")

    check_budget()

    processed_path, temp_path = preprocess_for_transcription(audio_path)
    total_duration = effective_duration_sec(processed_path)

    try:
        if settings.whisper_configured:
            return _transcribe_via_whisper(
                processed_path,
                total_duration,
                on_partial,
                fallback_transcript,
                audio_path.name,
            )

        chunk_specs, chunk_tmp = split_audio_into_chunks(
            processed_path,
            CHUNK_DURATION_SEC,
            min_duration_to_chunk=MIN_DURATION_TO_CHUNK_SEC,
        )
        multi_chunk = len(chunk_specs) > 1

        all_words: list[WordTimestamp] = []
        transcript_parts: list[str] = []
        total_cost = 0.0

        try:
            for i, (chunk_path, offset, chunk_dur) in enumerate(chunk_specs):
                part = _transcribe_chunk(chunk_path, chunk_dur)
                transcript_parts.append(part)
                chunk_words = align_transcript_to_timestamps(
                    part,
                    chunk_dur,
                    time_offset=offset,
                    index_offset=len(all_words),
                )
                all_words.extend(chunk_words)

                if on_partial:
                    partial_text = " ".join(transcript_parts)
                    on_partial(
                        _reindex_words(all_words),
                        partial_text,
                        i == len(chunk_specs) - 1,
                    )

                total_cost += estimate_gemini_audio_cost(chunk_dur)
        finally:
            if chunk_tmp and chunk_tmp.exists():
                shutil.rmtree(chunk_tmp, ignore_errors=True)

        transcript = " ".join(transcript_parts).strip()
        word_count = len(transcript.split())
        min_words = _min_words_for_duration(total_duration)
        if not transcript or word_count < min_words:
            live_result = _apply_live_fallback(
                fallback_transcript, total_duration, on_partial, audio_path.name
            )
            if live_result:
                return live_result
            raise ValueError(
                f"Transcription too short: Gemini returned {word_count} word(s) "
                f"({transcript!r}) for {total_duration:.1f}s of audio "
                f"(need at least {min_words})."
            )

        if multi_chunk:
            all_words = _reindex_words(all_words)

        record_cost(
            f"{get_provider().value}_transcription",
            f"Transcribe {audio_path.name} ({len(chunk_specs)} chunk(s))",
            total_cost,
        )

        return all_words, transcript, total_duration, "gemini"
    except Exception as exc:
        live_result = _apply_live_fallback(
            fallback_transcript, total_duration, on_partial, audio_path.name
        )
        if live_result:
            return live_result
        raise exc
    finally:
        if temp_path and temp_path.exists():
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
        # 0.8s pause here (hesitation before the filler)
        WordTimestamp(word="like", start=3.5, end=3.8, index=8),
        WordTimestamp(word="we", start=3.9, end=4.0, index=9),
        WordTimestamp(word="need", start=4.1, end=4.3, index=10),
        WordTimestamp(word="to", start=4.4, end=4.5, index=11),
        # 1.6s long pause here
        WordTimestamp(word="focus.", start=6.1, end=6.6, index=12),
    ]
    transcript = " ".join(w.word for w in mock_words)
    return mock_words, transcript, duration
