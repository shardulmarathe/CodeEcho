"""In-memory session store (v1). Replace with Supabase persistence later."""

import uuid
from threading import Lock

from app.models import SessionResult, SessionStatus

_sessions: dict[str, SessionResult] = {}
_lock = Lock()


def create_session(title: str = "Untitled Session") -> SessionResult:
    session_id = str(uuid.uuid4())
    session = SessionResult(
        session_id=session_id,
        status=SessionStatus.PENDING,
        title=title,
    )
    with _lock:
        _sessions[session_id] = session
    return session


def get_session(session_id: str) -> SessionResult | None:
    with _lock:
        return _sessions.get(session_id)


def update_session(session: SessionResult) -> SessionResult:
    with _lock:
        _sessions[session.session_id] = session
    return session


def list_sessions() -> list[SessionResult]:
    with _lock:
        return list(_sessions.values())
