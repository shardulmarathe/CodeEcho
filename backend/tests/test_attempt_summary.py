"""AttemptSummary enrichment + recording-cap helpers (in-memory, no Supabase)."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    DimensionScore,
    ScoreDimension,
    Scorecard,
    answer_cap_sec,
)
from app.services import session_store, store  # noqa: E402
from app.services.auth import Identity  # noqa: E402


def _force_in_memory() -> None:
    settings.supabase_service_role_key = ""
    settings.rerank_enabled = False
    settings.rag_enabled = False


def test_answer_cap_sec() -> None:
    assert answer_cap_sec("behavioral") == 180
    assert answer_cap_sec("technical", "coding") == 180
    assert answer_cap_sec("technical", None) == 180
    assert answer_cap_sec("technical", "project") == 300
    assert answer_cap_sec("technical", "system_design") == 300


def test_list_attempts_includes_score_and_metrics() -> None:
    _force_in_memory()
    session_store._sessions.clear()
    guest = "summary-guest-token"
    identity = Identity(guest_token=guest)
    session = store.create_attempt(identity, title="Scored practice")
    session.metrics.total_fillers = 4
    session.metrics.fillers_per_minute = 8.0
    session.metrics.words_per_minute = 120.0
    session.metrics.duration_sec = 30.0
    session_store.update_session(session)
    store.save_scorecard(
        Scorecard(
            attempt_id=session.session_id,
            rubric="experience",
            overall_score=3.2,
            overall_summary="ok",
            dimensions=[
                ScoreDimension(
                    dimension="Action",
                    score=2.0,
                    rationale="",
                    evidence="",
                    suggestion="",
                )
            ],
        )
    )
    rows = store.list_attempts(identity)
    assert len(rows) == 1
    row = rows[0]
    assert row.session_id == session.session_id
    assert row.total_fillers == 4
    assert row.fillers_per_minute == 8.0
    assert row.words_per_minute == 120.0
    assert row.overall_score == 3.2
    assert row.rubric == "experience"
    assert row.dimensions == [DimensionScore(dimension="Action", score=2.0)]
    assert session.max_duration_sec == 180


def test_create_attempt_design_cap() -> None:
    _force_in_memory()
    session_store._sessions.clear()
    from app.models import Question

    q = store.create_question(
        Question(
            id="q-design",
            qtype="technical",
            prompt="Design a URL shortener",
            meta={"track": "system_design"},
        )
    )
    identity = Identity(guest_token="cap-guest")
    session = store.create_attempt(identity, title="Design", question_id=q.id)
    assert session.max_duration_sec == 300


def test_create_attempt_returns_cap_via_api() -> None:
    _force_in_memory()
    session_store._sessions.clear()
    with TestClient(app) as client:
        response = client.post(
            "/api/attempts",
            headers={"X-Guest-Token": "api-cap-guest"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["max_duration_sec"] == 180


if __name__ == "__main__":
    tests = [
        test_answer_cap_sec,
        test_list_attempts_includes_score_and_metrics,
        test_create_attempt_design_cap,
        test_create_attempt_returns_cap_via_api,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"{len(tests) - failed} passed, {failed} failed")
    raise SystemExit(failed)
