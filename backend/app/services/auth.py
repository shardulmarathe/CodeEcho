"""Clerk authentication — verifies Clerk session JWTs against Clerk's JWKS.

Backend-mediated model: the frontend authenticates with Clerk and sends the
session token as `Authorization: Bearer <jwt>`. Guests instead send a
client-generated `X-Guest-Token` header. We verify the Clerk token's RS256
signature using Clerk's published JWKS and trust the `sub` claim as the user id.
"""

from dataclasses import dataclass
from typing import Optional

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from app.config import settings
from app.services import usage

_jwks_client: Optional[PyJWKClient] = None
_jwks_url: str = ""


@dataclass
class Identity:
    """Who is making the request — a logged-in Clerk user or an anonymous guest."""

    user_id: Optional[str] = None
    guest_token: Optional[str] = None

    @property
    def is_user(self) -> bool:
        return self.user_id is not None

    @property
    def is_guest(self) -> bool:
        return self.user_id is None and self.guest_token is not None


def clerk_configured() -> bool:
    return bool(settings.effective_clerk_jwks_url)


def _get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client, _jwks_url
    url = settings.effective_clerk_jwks_url
    if not url:
        return None
    if _jwks_client is None or _jwks_url != url:
        _jwks_client = PyJWKClient(url, cache_keys=True)
        _jwks_url = url
    return _jwks_client


def verify_clerk_token(token: str) -> str:
    """Verify a Clerk session JWT and return the Clerk user id (`sub`)."""
    client = _get_jwks_client()
    if client is None:
        raise HTTPException(status_code=503, detail="Auth is not configured (CLERK_ISSUER unset).")
    try:
        signing_key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer or None,
            options={
                "verify_aud": False,  # Clerk session tokens have no audience by default
                "verify_iss": bool(settings.clerk_issuer),
            },
        )
    except HTTPException:
        raise
    except Exception as exc:  # invalid signature / expired / malformed
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {exc}")

    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token is missing a subject claim.")
    return sub


def _bearer_token(request: Request) -> Optional[str]:
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


async def get_current_user(request: Request) -> str:
    """FastAPI dependency: require a valid Clerk user; return the user id."""
    token = _bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return verify_clerk_token(token)


async def get_optional_identity(request: Request) -> Identity:
    """FastAPI dependency: resolve a logged-in user OR a guest token.

    A present-but-invalid bearer token still raises 401 (no silent downgrade).
    """
    token = _bearer_token(request)
    if token:
        identity = Identity(user_id=verify_clerk_token(token))
    else:
        guest = request.headers.get("x-guest-token")
        identity = Identity(guest_token=guest.strip() if guest else None)
    # Bill/throttle budget against this caller (user id, or IP for guests/anon).
    usage.set_subject(usage.subject_string(request, identity))
    return identity
