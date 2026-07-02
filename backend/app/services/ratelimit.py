"""Shared slowapi limiter. Wired into the app in main.py and applied to expensive
endpoints in routes.py.

The default limit is keyed per client IP. Expensive endpoints instead use
``expensive_key``: a valid signed-in user is throttled by their Clerk id (so they
can't multiply their quota by switching IPs), and everyone else by IP. Guest
tokens are deliberately NOT used as a key — they're client-minted and rotatable.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services import usage
from app.services.auth import _bearer_token, verify_clerk_token

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)


def expensive_key(request) -> str:
    """Throttle signed-in users by Clerk id, everyone else by IP."""
    token = _bearer_token(request)
    if token:
        try:
            return f"user:{verify_clerk_token(token)}"
        except Exception:
            pass  # invalid/expired token: the route dependency will 401 it
    return usage.ip_subject(request)
