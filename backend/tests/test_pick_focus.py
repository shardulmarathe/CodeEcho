"""Weakest-dimension targeting for question generation and interview plans."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.models import Question, ScoreDimension, Scorecard  # noqa: E402
from app.services import session_store, store  # noqa: E402
from app.services.auth import Identity  # noqa: E402
from app.services.interview import build_plan  # noqa: E402
from app.services.questions import pick_focus  # noqa: E402


def _force_in_memory() -> None:
    settings.supabase_service_role_key = ""
    settings.rerank_enabled = False
    settings.rag_enabled = False
    session_store._sessions.clear()
    store._mem_questions.clear()
    store._mem_scorecards.clear()
    store._mem_interviews.clear()


def _dim(name: str, score: float) -> ScoreDimension:
    return ScoreDimension(
        dimension=name, score=score, rationale="", evidence="", suggestion=""
    )


def _scored(
    identity: Identity,
    overall: float,
    dims: list[ScoreDimension],
    *,
    qtype: str = "behavioral",
    bucket: str | None = None,
    track: str | None = None,
) -> None:
    q = store.create_question(
        Question(
            id=__import__("uuid").uuid4().hex,
            qtype=qtype,
            prompt="seed",
            meta={k: v for k, v in (("bucket", bucket), ("track", track)) if v},
        )
    )
    session = store.create_attempt(identity, title="scored", question_id=q.id)
    store.save_scorecard(
        Scorecard(
            attempt_id=session.session_id,
            rubric=bucket or track or qtype,
            overall_score=overall,
            dimensions=dims,
        )
    )


def test_pick_focus_none_under_three_scored() -> None:
    _force_in_memory()
    identity = Identity(guest_token="focus-guest")
    assert pick_focus(identity) is None
    _scored(identity, 3.0, [_dim("Action", 2.0)], bucket="experience")
    _scored(identity, 3.0, [_dim("Action", 2.0)], bucket="experience")
    assert pick_focus(identity) is None


def test_pick_focus_skips_delivery_and_picks_action() -> None:
    _force_in_memory()
    identity = Identity(guest_token="focus-guest-2")
    for _ in range(3):
        _scored(
            identity,
            3.0,
            [_dim("Delivery", 1.0), _dim("Conciseness", 1.0), _dim("Action", 2.0)],
            bucket="experience",
        )
    focus = pick_focus(identity)
    assert focus is not None
    assert focus["dimension"] == "Action"
    assert focus["bucket"] == "experience"
    assert "competency" not in focus


def test_communication_only_when_system_design() -> None:
    _force_in_memory()
    coding = Identity(guest_token="focus-coding")
    for _ in range(3):
        _scored(
            coding,
            3.0,
            [_dim("Communication", 1.0), _dim("Correctness", 4.0)],
            qtype="technical",
            track="coding",
        )
    focus = pick_focus(coding)
    assert focus is not None
    assert focus["dimension"] == "Correctness"
    assert focus["track"] == "coding"

    design = Identity(guest_token="focus-design")
    for _ in range(3):
        _scored(
            design,
            3.0,
            [_dim("Communication", 1.0), _dim("Trade-offs", 5.0)],
            qtype="technical",
            track="system_design",
        )
    focus = pick_focus(design)
    assert focus is not None
    assert focus["dimension"] == "Communication"
    assert focus["track"] == "system_design"


def test_build_plan_puts_focused_bucket_first() -> None:
    _force_in_memory()
    identity = Identity(guest_token="focus-plan")
    for _ in range(3):
        _scored(
            identity,
            3.0,
            [_dim("Action", 1.5), _dim("Delivery", 5.0)],
            bucket="experience",
        )
    plan = build_plan("behavioral", None, 3, identity)
    assert [s.bucket for s in plan] == ["experience", "introspection", "learning"]
    assert plan[0].focus == "Action"
    assert plan[1].focus is None
    assert plan[2].focus is None


if __name__ == "__main__":
    tests = [
        test_pick_focus_none_under_three_scored,
        test_pick_focus_skips_delivery_and_picks_action,
        test_communication_only_when_system_design,
        test_build_plan_puts_focused_bucket_first,
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
