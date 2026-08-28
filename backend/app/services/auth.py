"""Supabase Auth — verify access tokens, resolve user or guest identity.

Backend-mediated model: the frontend signs in with Supabase Auth and sends
``Authorization: Bearer <access_token>``. Guests send a client-generated
``X-Guest-Token`` header.

Tokens are verified from the ``alg`` header:
  - ES256 / RS256: JWKS at ``{SUPABASE_URL}/auth/v1/.well-known/jwks.json``
    (current Supabase signing keys; no extra env).
  - HS256: ``SUPABASE_JWT_SECRET`` if set (legacy shared secret / tests).

FastAPI is the PEP; Postgres is queried with the service-role key scoped by
this Identity.
"""

from dataclasses import dataclass
from typing import Optional

import jwt
from fastapi import HTTPException, Request

from app.config import settings
from app.services import usage

_jwks_clients: dict[str, jwt.PyJWKClient] = {}


@dataclass
class Identity:
    """Who is making the request — a signed-in Supabase user or an anonymous guest."""

    user_id: Optional[str] = None
    guest_token: Optional[str] = None
    email: Optional[str] = None

    @property
    def is_user(self) -> bool:
        return self.user_id is not None

    @property
    def is_guest(self) -> bool:
        return self.user_id is None and self.guest_token is not None


def auth_configured() -> bool:
    """True when we can verify access tokens: JWKS via project URL, or HS256 secret."""
    return bool(settings.supabase_url) or bool(settings.supabase_jwt_secret)


def _bearer_token(request: Request) -> Optional[str]:
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


def _guest_header(request: Request) -> Optional[str]:
    guest = request.headers.get("x-guest-token")
    return guest.strip() if guest else None


def _issuer() -> str:
    return settings.supabase_url.rstrip("/") + "/auth/v1"


def _jwks_client() -> jwt.PyJWKClient:
    url = _issuer() + "/.well-known/jwks.json"
    client = _jwks_clients.get(url)
    if client is None:
        client = jwt.PyJWKClient(url, cache_jwk_set=True, lifespan=3600)
        _jwks_clients[url] = client
    return client


def _decode_hs256(token: str) -> dict:
    if not settings.supabase_jwt_secret:
        raise jwt.InvalidTokenError("HS256 token but SUPABASE_JWT_SECRET is unset.")
    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience="authenticated",
        issuer=_issuer(),
    )


def _decode_jwks(token: str) -> dict:
    if not settings.supabase_url:
        raise jwt.InvalidTokenError("Asymmetric token but SUPABASE_URL is unset.")
    key = _jwks_client().get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        key,
        algorithms=["ES256", "RS256"],
        audience="authenticated",
        issuer=_issuer(),
    )


def verify_access_token(token: str) -> tuple[str, Optional[str]]:
    """Verify a Supabase Auth access token and return ``(sub, email)``."""
    if not auth_configured():
        raise HTTPException(
            status_code=503,
            detail="Auth is not configured (SUPABASE_URL unset).",
        )
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        if alg == "HS256":
            claims = _decode_hs256(token)
        else:
            claims = _decode_jwks(token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {exc}")

    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token is missing a subject claim.")
    email = claims.get("email")
    return str(sub), email if isinstance(email, str) else None


def resolve_identity(request: Request) -> Identity:
    """Resolve identity once per request and cache on ``request.state``.

    A present-but-invalid bearer token still raises 401 (no silent downgrade).
    """
    cached = getattr(request.state, "identity", None)
    if cached is not None:
        return cached

    token = _bearer_token(request)
    if token:
        user_id, email = verify_access_token(token)
        identity = Identity(user_id=user_id, email=email)
    else:
        identity = Identity(guest_token=_guest_header(request))
    request.state.identity = identity
    return identity


async def get_current_user(request: Request) -> str:
    """FastAPI dependency: require a valid signed-in user; return the user id."""
    identity = resolve_identity(request)
    if not identity.user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return identity.user_id


async def get_optional_identity(request: Request) -> Identity:
    """FastAPI dependency: resolve a logged-in user OR a guest token."""
    identity = resolve_identity(request)
    usage.set_subject(usage.subject_string(request, identity))
    return identity
