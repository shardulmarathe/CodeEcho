"""Audio storage — durable copy in a private Supabase bucket (served via signed
URLs), plus a local-disk copy that the analysis pipeline reads (ffmpeg/Gemini
need a real file path). Falls back to local-only when Supabase is unconfigured.
"""

from pathlib import Path
from typing import Optional

from app.config import settings
from app.services import supabase_client

SIGNED_URL_TTL_SEC = 60 * 60  # 1 hour

_CONTENT_TYPES = {
    ".webm": "audio/webm",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".mp4": "audio/mp4",
}


def _content_type(ext: str) -> str:
    return _CONTENT_TYPES.get(ext.lower(), "application/octet-stream")


def _local_path(filename: str) -> Path:
    directory = Path(settings.upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename


def save_audio(attempt_id: str, content: bytes, ext: str) -> tuple[Path, str]:
    """Write audio to local disk (for processing) and, if configured, the private
    Supabase bucket (for durable storage). Returns (local_path, storage_key)."""
    filename = f"{attempt_id}{ext}"
    local = _local_path(filename)
    local.write_bytes(content)

    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            client.storage.from_(settings.supabase_storage_bucket).upload(
                filename,
                content,
                {"content-type": _content_type(ext), "upsert": "true"},
            )
        except Exception:
            # Durable upload is best-effort; never fail the request over it.
            pass

    return local, filename


def audio_url(storage_key: Optional[str]) -> str:
    """A URL the frontend can play: a short-lived signed URL (Supabase) or the
    local serving route as a fallback."""
    if not storage_key:
        return ""
    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            res = client.storage.from_(settings.supabase_storage_bucket).create_signed_url(
                storage_key, SIGNED_URL_TTL_SEC
            )
            return res.get("signedURL") or res.get("signedUrl") or ""
        except Exception:
            pass
    return f"/api/audio/{storage_key}"


def local_audio_file(filename: str) -> Optional[Path]:
    path = _local_path(filename)
    return path if path.exists() else None


# Extensions we may have stored (see ALLOWED_EXTENSIONS in routes.py).
_KNOWN_EXTS = [".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4"]


def ensure_local_audio(attempt_id: str) -> Optional[Path]:
    """Return a local path to the attempt's audio, re-downloading it from the
    Supabase bucket if the local copy is gone.

    On ephemeral-disk hosts (e.g. Render) the local file written at upload time
    does not survive a restart, but the durable Supabase copy does. This lets a
    later (re)analysis still find the audio. Returns None if it can't be located.
    """
    existing = list(Path(settings.upload_dir).glob(f"{attempt_id}.*"))
    if existing:
        return existing[0]

    if not supabase_client.is_configured():
        return None

    try:
        client = supabase_client.get_client()
        bucket = client.storage.from_(settings.supabase_storage_bucket)
        for ext in _KNOWN_EXTS:
            key = f"{attempt_id}{ext}"
            try:
                data = bucket.download(key)
            except Exception:
                data = None
            if data:
                local = _local_path(key)
                local.write_bytes(data)
                return local
    except Exception:
        return None
    return None
