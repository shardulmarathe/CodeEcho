"""Guest accounts: anonymous users get a guest token so they can use the app without
signing in. There is no usage cap — the global API budget (see services/budget.py) and
per-IP rate limiting are the cost guards. On signup a guest's attempts are transferred to
their account via ``claim()``.
"""

from app.services import supabase_client
from app.services.auth import Identity


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
            client.table("guests").upsert(
                {"guest_token": guest_token, "claimed_by_user_id": user_id}
            ).execute()
            return len(res.data or [])
        except Exception:
            return 0

    # In-memory fallback
    from app.services import session_store

    count = 0
    for s in session_store.list_sessions():
        if s.guest_token == guest_token:
            s.user_id = user_id
            s.guest_token = None
            session_store.update_session(s)
            count += 1
    return count
