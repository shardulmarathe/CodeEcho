"""Retrieved-source provenance and rubric definitions on scorecards."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.models import KBDocument  # noqa: E402
from app.services import scoring  # noqa: E402


def test_retrieve_reference_returns_exact_kb_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    doc = KBDocument(
        id="chunk-42",
        ref="fallback.pdf",
        content="  Use a concrete result and explain the impact.  ",
        meta={
            "title": "Behavioral Interview Guide",
            "canonical_url": "https://example.org/behavioral-guide",
        },
    )
    monkeypatch.setattr(scoring.kb_store, "retrieve_similar", lambda *args, **kwargs: [doc])

    reference, sources = scoring._retrieve_reference("Tell me about impact", "experience")

    assert reference == "- Use a concrete result and explain the impact."
    assert [source.model_dump() for source in sources] == [
        {
            "id": "chunk-42",
            "title": "Behavioral Interview Guide",
            "url": "https://example.org/behavioral-guide",
            "snippet": "Use a concrete result and explain the impact.",
        }
    ]


@pytest.mark.parametrize("result", [[], RuntimeError("embedding unavailable")])
def test_empty_or_failed_retrieve_is_rubric_only(
    monkeypatch: pytest.MonkeyPatch, result: object
) -> None:
    def retrieve(*args, **kwargs):
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(scoring.kb_store, "retrieve_similar", retrieve)

    assert scoring._retrieve_reference("question", "coding") == ("", [])


def test_scorecard_serializes_definitions_and_sources() -> None:
    source = scoring.ScoreSource(
        id="chunk-1", title="Guide", url=None, snippet="Relevant guidance"
    )
    card = scoring._build_scorecard(
        "attempt-1",
        "technical",
        {
            "overall_summary": "Clear approach.",
            "dimensions": [
                {
                    "dimension": "Correctness",
                    "score": 4,
                    "rationale": "Sound.",
                    "evidence": "hash map",
                    "suggestion": "Prove the invariant.",
                }
            ],
        },
        [("Correctness", "is the described approach actually correct?")],
        [source],
    )

    payload = card.model_dump()
    assert payload["sources"] == [source.model_dump()]
    assert payload["dimension_definitions"] == [
        {
            "name": "Correctness",
            "description": "is the described approach actually correct?",
        }
    ]
