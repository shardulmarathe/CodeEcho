"""Guest accounts: anonymous users get a guest token so they can use the app without
signing in. There is no usage cap — the global API budget (see services/budget.py) and
per-IP rate limiting are the cost guards. On signup a guest's attempts are transferred to
their account via ``claim()``.
"""

from app.services import supabase_client


def _claim_memory(user_id: str, guest_token: str) -> int:
    """Patch the live in-process cache so get_attempt sees the new owner immediately."""
    from app.services import session_store
    from app.services.store import _mem_interviews, _mem_questions

    count = 0
    for s in session_store.list_sessions():
        if s.guest_token == guest_token:
            s.user_id = user_id
            s.guest_token = None
            session_store.update_session(s)
            count += 1
    for s in _mem_interviews.values():
        if s.guest_token == guest_token:
            s.user_id = user_id
            s.guest_token = None
    for q in _mem_questions.values():
        if (q.meta or {}).get("_guest_token") == guest_token:
            q.owner_user_id = user_id
            q.meta.pop("_guest_token", None)
    return count


def claim(user_id: str, guest_token: str) -> int:
    """Transfer a guest's attempts to a logged-in user. Returns count transferred."""
    if not guest_token:
        return 0

    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            res = (
                client.table("attempts")
                .update({"user_id": user_id, "guest_token": None})
                .eq("guest_token", guest_token)
                .execute()
            )
            client.table("interview_sessions").update(
                {"user_id": user_id, "guest_token": None}
            ).eq("guest_token", guest_token).execute()
            try:
                client.table("questions").update({"owner_user_id": user_id}).filter(
                    "meta->>_guest_token", "eq", guest_token
                ).execute()
            except Exception:
                pass
            client.table("guests").upsert(
                {"guest_token": guest_token, "claimed_by_user_id": user_id}
            ).execute()
            # Cache first: get_attempt returns the live row without hitting Postgres.
            _claim_memory(user_id, guest_token)
            return len(res.data or [])
        except Exception:
            return 0

    return _claim_memory(user_id, guest_token)
