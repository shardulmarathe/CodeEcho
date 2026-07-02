"""Supabase client — a single cached service-role client for the backend."""

from app.config import settings

_client = None


def is_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def get_client():
    """Return a cached Supabase client. Cached because hot paths (budget
    accounting) call this per request and recreating a client each time is wasteful."""
    global _client
    if not is_configured():
        raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    if _client is None:
        from supabase import create_client

        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client
