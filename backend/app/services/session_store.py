"""In-memory live session cache.

The analysis pipeline writes here during streaming; `store.py` reads it before falling
back to Supabase. Bounded (LRU) so a warm, never-sleeping process cannot grow without
limit — see `bounded_cache` for why that stopped being self-correcting.

SessionResult is the heaviest cached object (per-word timestamps for a 3-5 minute
answer), so this bound is much tighter than the metadata caches in `store.py`.
"""

import uuid

from app.models import SessionResult, SessionStatus
from app.services.bounded_cache import BoundedCache

_sessions: BoundedCache[str, SessionResult] = BoundedCache(200)


def create_session(title: str = "Untitled Session") -> SessionResult:
    session_id = str(uuid.uuid4())
    session = SessionResult(
        session_id=session_id,
        status=SessionStatus.PENDING,
        title=title,
    )
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> SessionResult | None:
    return _sessions.get(session_id)


def update_session(session: SessionResult) -> SessionResult:
    _sessions[session.session_id] = session
    return session


def list_sessions() -> list[SessionResult]:
    return _sessions.values()
