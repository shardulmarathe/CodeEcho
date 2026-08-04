"""Pause detection for communication analysis.

A pause is a stretch of silence in the delivery. We detect real silence from the
audio waveform (ffmpeg ``silencedetect``) because the transcription model returns
*contiguous* word timestamps, each word's end equals the next word's start, so
inter-word gaps are always zero and cannot reveal pauses. The detected silences are
then mapped onto the transcript by time so they can be shown inline.

The inter-word-gap method is kept as a fallback for inputs whose timestamps *do*
contain gaps (e.g. the offline mock transcript).
"""

import shutil
import subprocess
from pathlib import Path

from app.models import PauseOccurrence, WordTimestamp

# Minimum silence (seconds) surfaced as a pause. Below this is normal speech rhythm.
PAUSE_THRESHOLD_SEC = 0.6

# Silence at or above this reads as a notably long hesitation worth flagging on its own.
LONG_PAUSE_SEC = 1.5

# Anything quieter than this is treated as silence. Speech peaks are typically well
# above -30 dB; room tone / held breath sits below it.
SILENCE_NOISE_DB = -30


def detect_pauses(
    words: list[WordTimestamp],
    audio_path: Path | None = None,
    threshold: float = PAUSE_THRESHOLD_SEC,
) -> list[PauseOccurrence]:
    """Detect pauses, preferring real silence from ``audio_path``.

    Falls back to inter-word timestamp gaps when no audio is given or ffmpeg silence
    detection is unavailable / yields nothing.
    """
    if audio_path is not None:
        silences = _detect_silences_ffmpeg(audio_path, threshold)
        if silences is not None:
            return _map_silences_to_words(silences, words)
    return _gap_pauses(words, threshold)


def _detect_silences_ffmpeg(
    audio_path: Path, min_duration: float
) -> list[tuple[float, float, float]] | None:
    """Return [(start, end, duration), ...] of silent spans, or None on failure."""
    if not audio_path.exists() or not shutil.which("ffmpeg"):
        return None
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(audio_path),
                "-af",
                f"silencedetect=noise={SILENCE_NOISE_DB}dB:d={min_duration}",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (subprocess.SubprocessError, OSError):
        return None

    silences: list[tuple[float, float, float]] = []
    pending_start: float | None = None
    for line in (result.stderr or "").splitlines():
        if "silence_start:" in line:
            try:
                pending_start = float(line.split("silence_start:")[1].strip())
            except (ValueError, IndexError):
                pending_start = None
        elif "silence_end:" in line and pending_start is not None:
            try:
                end = float(line.split("silence_end:")[1].split("|")[0].strip())
            except (ValueError, IndexError):
                pending_start = None
                continue
            duration = round(end - pending_start, 2)
            if duration >= min_duration:
                silences.append((pending_start, end, duration))
            pending_start = None
    return silences


def _map_silences_to_words(
    silences: list[tuple[float, float, float]], words: list[WordTimestamp]
) -> list[PauseOccurrence]:
    """Attribute each silence to the word the speaker was on when it began."""
    if not words:
        return []
    first_start = words[0].start
    last_end = words[-1].end

    pauses: list[PauseOccurrence] = []
    for s_start, s_end, duration in silences:
        # Skip leading/trailing dead air outside the spoken range.
        if s_end <= first_start or s_start >= last_end:
            continue
        # The word being spoken (or just finished) when the silence began.
        after_index = 0
        for i, w in enumerate(words):
            if w.start <= s_start:
                after_index = i
            else:
                break
        pauses.append(
            PauseOccurrence(
                start=round(s_start, 2),
                end=round(s_end, 2),
                duration=duration,
                after_index=after_index,
                is_long=duration >= LONG_PAUSE_SEC,
            )
        )
    return pauses


def _gap_pauses(
    words: list[WordTimestamp], threshold: float
) -> list[PauseOccurrence]:
    """Fallback: surface silent gaps between consecutive word timestamps."""
    pauses: list[PauseOccurrence] = []
    for i in range(1, len(words)):
        gap = words[i].start - words[i - 1].end
        if gap >= threshold:
            pauses.append(
                PauseOccurrence(
                    start=words[i - 1].end,
                    end=words[i].start,
                    duration=round(gap, 2),
                    after_index=i - 1,
                    is_long=gap >= LONG_PAUSE_SEC,
                )
            )
    return pauses
