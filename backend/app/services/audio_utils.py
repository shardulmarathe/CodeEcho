"""Audio file utilities."""

import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

MIN_CHUNK_BYTES = 1000
MIN_CHUNK_DURATION_SEC = 0.5


class AudioValidationError(ValueError):
    """Audio is empty/silent/too quiet — carries a user-safe message to show + retry."""


def get_audio_duration_sec(audio_path: Path) -> float | None:
    """Get audio duration in seconds using ffprobe, wave, or None."""
    suffix = audio_path.suffix.lower()

    if suffix == ".wav":
        try:
            with wave.open(str(audio_path), "rb") as wf:
                return wf.getnframes() / float(wf.getframerate())
        except Exception:
            pass

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            duration = float(result.stdout.strip())
            if duration > 0:
                return duration
    except Exception:
        pass

    return None


def effective_duration_sec(
    audio_path: Path, words_end: float | None = None
) -> float:
    """Best available duration: prefer actual audio file length."""
    file_duration = get_audio_duration_sec(audio_path)
    if file_duration and file_duration > 0:
        return file_duration
    if words_end and words_end > 0:
        return words_end
    return 1.0


def _measure_volume_db(audio_path: Path) -> tuple[float | None, float | None]:
    """Return (mean_volume_db, peak_volume_db) for PCM WAV, else ffmpeg fallback."""
    if audio_path.suffix.lower() == ".wav":
        try:
            with wave.open(str(audio_path), "rb") as wf:
                sample_width = wf.getsampwidth()
                frames = wf.readframes(wf.getnframes())
            if not frames or sample_width != 2:
                return None, None
            count = len(frames) // 2
            if count == 0:
                return None, None
            samples = struct.unpack(f"<{count}h", frames)
            peak = max(abs(s) for s in samples)
            if peak == 0:
                return -91.0, -91.0
            rms = math.sqrt(sum(s * s for s in samples) / count)
            mean_db = 20.0 * math.log10(rms / 32768.0)
            peak_db = 20.0 * math.log10(peak / 32768.0)
            return mean_db, peak_db
        except Exception:
            pass

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(audio_path),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        stderr = result.stderr or ""
        mean_db: float | None = None
        max_db: float | None = None
        for line in stderr.splitlines():
            if "mean_volume:" in line:
                try:
                    mean_db = float(line.split("mean_volume:")[1].split("dB")[0].strip())
                except ValueError:
                    pass
            if "max_volume:" in line:
                try:
                    max_db = float(line.split("max_volume:")[1].split("dB")[0].strip())
                except ValueError:
                    pass
        return mean_db, max_db
    except Exception:
        return None, None


def validate_audio_signal(audio_path: Path) -> None:
    """Fail fast if audio is too short, empty, or likely silent."""
    if not audio_path.exists():
        raise ValueError("Audio file not found")

    size = audio_path.stat().st_size
    if size < MIN_CHUNK_BYTES:
        raise AudioValidationError(
            "That recording was too short — record at least 2–3 seconds and try again."
        )

    duration = get_audio_duration_sec(audio_path)
    if duration is not None and duration < 1.0:
        raise AudioValidationError(
            "That recording was too short — record at least 2–3 seconds and try again."
        )

    mean_db, max_db = _measure_volume_db(audio_path)
    # ffmpeg reports -91 dB for digital silence; speech is typically > -45 dB max.
    if max_db is not None and max_db <= -60.0:
        raise AudioValidationError(
            "No audio was picked up from your mic. Check your input device "
            "(System Settings → Sound → Input), then record again."
        )
    if mean_db is not None and mean_db <= -70.0 and (max_db is None or max_db <= -55.0):
        raise AudioValidationError(
            "Your recording was too quiet to hear. Move closer to the mic and record again."
        )


def preprocess_for_transcription(audio_path: Path) -> tuple[Path, Path | None]:
    """Always convert audio to 16kHz mono PCM WAV for reliable STT."""
    if not shutil.which("ffmpeg"):
        raise ValueError(
            "ffmpeg is required for audio transcription. Install it with: brew install ffmpeg"
        )

    tmp_dir = Path(tempfile.mkdtemp(prefix="codeecho_audio_"))
    tmp = tmp_dir / "transcribe_input.wav"
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(audio_path),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(tmp),
            ],
            capture_output=True,
            check=True,
            timeout=120,
        )
        if not tmp.exists() or tmp.stat().st_size < 100:
            raise ValueError("Audio conversion produced an empty file")
        validate_audio_signal(tmp)
        return tmp, tmp_dir
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or b"").decode("utf-8", errors="replace")[:300]
        raise ValueError(f"Could not convert audio for transcription: {stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise ValueError("Audio conversion timed out") from e


def _is_valid_chunk(chunk_path: Path, expected_duration: float) -> bool:
    if not chunk_path.exists():
        return False
    if chunk_path.stat().st_size < MIN_CHUNK_BYTES:
        return False
    actual = get_audio_duration_sec(chunk_path)
    if actual is None or actual < MIN_CHUNK_DURATION_SEC:
        return False
    if expected_duration >= 1.0 and actual < expected_duration * 0.5:
        return False
    return True


def split_audio_into_chunks(
    audio_path: Path,
    chunk_sec: float = 15.0,
    *,
    min_duration_to_chunk: float = 30.0,
) -> tuple[list[tuple[Path, float, float]], Path | None]:
    """
    Split audio into segments for chunked transcription.
    Skips chunking when total duration is below min_duration_to_chunk.
    """
    duration = get_audio_duration_sec(audio_path)
    if not duration or duration <= min_duration_to_chunk:
        return [(audio_path, 0.0, duration or chunk_sec)], None

    if not shutil.which("ffmpeg"):
        return [(audio_path, 0.0, duration)], None

    tmp_dir = Path(tempfile.mkdtemp(prefix="codeecho_chunks_"))
    chunks: list[tuple[Path, float, float]] = []
    start = 0.0
    index = 0

    while start < duration - 0.1:
        seg_dur = min(chunk_sec, duration - start)
        chunk_path = tmp_dir / f"chunk_{index:03d}.wav"
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(audio_path),
                    "-ss",
                    str(start),
                    "-t",
                    str(seg_dur),
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(chunk_path),
                ],
                capture_output=True,
                check=True,
                timeout=60,
            )
            if _is_valid_chunk(chunk_path, seg_dur):
                chunks.append((chunk_path, start, seg_dur))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        start += chunk_sec
        index += 1

    if not chunks:
        return [(audio_path, 0.0, duration)], None

    return chunks, tmp_dir
