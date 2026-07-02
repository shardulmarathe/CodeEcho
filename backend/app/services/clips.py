"""Generate audio clips around filler occurrences using FFmpeg."""

import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.models import FillerOccurrence


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def generate_clip(
    audio_path: Path,
    filler: FillerOccurrence,
    session_id: str,
    output_dir: Path,
) -> str | None:
    """Extract ±clip_padding_sec around filler. Returns relative clip path."""
    if not _ffmpeg_available():
        return None

    padding = settings.clip_padding_sec
    start = max(0, filler.start - padding)
    duration = (filler.end - filler.start) + (2 * padding)

    output_dir.mkdir(parents=True, exist_ok=True)
    clip_name = f"{session_id}_{filler.index}.mp3"
    clip_path = output_dir / clip_name

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
                str(duration),
                "-acodec",
                "libmp3lame",
                "-q:a",
                "4",
                str(clip_path),
            ],
            capture_output=True,
            check=True,
            timeout=30,
        )
        return f"/clips/{clip_name}"
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def generate_all_clips(
    audio_path: Path,
    fillers: list[FillerOccurrence],
    session_id: str,
    clips_dir: Path,
) -> list[FillerOccurrence]:
    """Generate clips for all fillers and attach clip URLs."""
    for filler in fillers:
        clip_url = generate_clip(audio_path, filler, session_id, clips_dir)
        filler.clip_url = clip_url
    return fillers
