"""Shared slowapi limiter. Wired into the app in main.py and applied to expensive
endpoints in routes.py.

The default limit is keyed per client IP. Expensive endpoints instead use
``expensive_key``: a valid signed-in user is throttled by their user id (so they
can't multiply their quota by switching IPs), and everyone else by IP. Guest
tokens are deliberately NOT used as a key — they're client-minted and rotatable.
"""

from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services import usage
from app.services.auth import resolve_identity

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)


def expensive_key(request) -> str:
    """Throttle signed-in users by user id, everyone else by IP."""
    try:
        identity = resolve_identity(request)
        if identity.is_user:
            return f"user:{identity.user_id}"
    except HTTPException:
        pass  # invalid/expired token: the route dependency will 401 it
    return usage.ip_subject(request)
