"""Per-request usage identity ("subject") for budget accounting and rate limiting.

A *subject* is who to bill/throttle a request against:
  - ``user:<id>`` for a signed-in user, or
  - ``ip:<addr>``       for a guest / anonymous caller.

Guests are keyed by IP, NOT by their ``X-Guest-Token`` — guest tokens are minted
client-side and can be rotated for free, so keying limits on them would be useless.

The subject is stashed in a ``ContextVar`` so the deep budget call sites
(scoring / transcribe / questions / transition) can read it without every
function signature having to thread it through. It is set once per request by the
auth dependency (see ``auth.get_optional_identity``), including analyze and stream.
"""

import contextvars
from typing import Optional

from slowapi.util import get_remote_address

# None until a request sets it; deep call sites treat None as "global only".
_subject: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "budget_subject", default=None
)


def ip_subject(request) -> str:
    return f"ip:{get_remote_address(request)}"


def subject_string(request, identity=None) -> str:
    """Resolve the billing/throttle subject for a request.

    Signed-in users are keyed by user id (stable across IPs); everyone else by IP.
    """
    if identity is not None and getattr(identity, "is_user", False):
        return f"user:{identity.user_id}"
    return ip_subject(request)


def set_subject(subject: Optional[str]) -> None:
    _subject.set(subject)


def get_subject() -> Optional[str]:
    return _subject.get()
