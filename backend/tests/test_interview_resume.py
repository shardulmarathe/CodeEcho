"""GET /interviews/{id}/current — the resume path.

An interview is an immutable plan plus an append-only turns log, and every cursor
is derived from that log. Resume leans on exactly that property: it reads the
pending turn rather than storing "where you were", so it cannot disagree with the
log and cannot advance the interview by being called.

Runs fully offline: no LLM key means questions come from the mock banks, and no
service-role key means the in-memory store.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402


def _offline() -> None:
    settings.gemini_api_key = ""          # -> mock question banks
    settings.supabase_service_role_key = ""  # -> in-memory store
    settings.rag_enabled = False
    settings.rerank_enabled = False


def _guest() -> dict[str, str]:
    return {"X-Guest-Token": str(uuid.uuid4())}


def _start(client: TestClient, headers: dict[str, str]) -> dict:
    r = client.post(
        "/api/interviews",
        json={"mode": "behavioral", "seniority": "mid", "num_behavioral": 3},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_current_returns_the_unanswered_turn():
    _offline()
    with TestClient(app) as client:
        headers = _guest()
        started = _start(client, headers)

        r = client.get(f"/api/interviews/{started['session_id']}/current", headers=headers)
        assert r.status_code == 200, r.text
        body = r.json()

        # Same turn and question the interview opened on, so a resumed client can
        # render it with the identical code path it uses for start/advance.
        assert body["done"] is False
        assert body["turn_id"] == started["turn_id"]
        assert body["question"]["id"] == started["question"]["id"]
        assert body["progress"] == started["progress"]


def test_current_is_read_only():
    _offline()
    with TestClient(app) as client:
        headers = _guest()
        started = _start(client, headers)
        sid = started["session_id"]

        before = client.get(f"/api/interviews/{sid}", headers=headers).json()
        for _ in range(3):
            client.get(f"/api/interviews/{sid}/current", headers=headers)
        after = client.get(f"/api/interviews/{sid}", headers=headers).json()

        # Polling resume must not append turns or otherwise advance the log.
        assert len(after["turns"]) == len(before["turns"]) == 1
        assert after["turns"][0]["turn_id"] == started["turn_id"]
        assert after["turns"][0]["answered"] is False


def test_current_is_scoped_to_the_owner():
    _offline()
    with TestClient(app) as client:
        started = _start(client, _guest())
        # A different guest must not be able to resume someone else's interview.
        r = client.get(
            f"/api/interviews/{started['session_id']}/current", headers=_guest()
        )
        assert r.status_code == 404, r.text


def test_current_requires_an_identity():
    _offline()
    with TestClient(app) as client:
        started = _start(client, _guest())
        r = client.get(f"/api/interviews/{started['session_id']}/current")
        assert r.status_code == 400, r.text


def test_unknown_interview_is_404():
    _offline()
    with TestClient(app) as client:
        r = client.get(f"/api/interviews/{uuid.uuid4()}/current", headers=_guest())
        assert r.status_code == 404, r.text
