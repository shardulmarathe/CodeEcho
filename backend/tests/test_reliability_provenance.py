"""Capability honesty and normalized question provenance."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Question  # noqa: E402
from app.services import questions  # noqa: E402
from app.services.budget import BudgetExceededError  # noqa: E402
from app.services.llm_client import LLMResult  # noqa: E402


def test_offline_generation_is_labeled_mock(monkeypatch) -> None:
    monkeypatch.setattr(questions, "is_configured", lambda: False)

    question = questions.generate_question(qtype="behavioral", bucket="experience")

    assert question.source == "mock"
    assert question.fallback_reason == "llm_unavailable"


def test_budget_fallback_is_labeled_mock(monkeypatch) -> None:
    monkeypatch.setattr(questions, "is_configured", lambda: True)

    def refuse_budget() -> None:
        raise BudgetExceededError("shared cap reached")

    monkeypatch.setattr(questions, "check_budget", refuse_budget)

    question = questions.generate_question(qtype="technical", track="coding")

    assert question.source == "mock"
    assert question.fallback_reason == "budget_exceeded"


def test_successful_generation_and_pasted_question_sources(monkeypatch) -> None:
    monkeypatch.setattr(questions, "is_configured", lambda: True)
    monkeypatch.setattr(questions, "check_budget", lambda: None)
    monkeypatch.setattr(
        questions,
        "chat_completion",
        lambda *args, **kwargs: LLMResult(
            '{"prompt":"Tell me about a production incident you owned.","topic":"ownership"}'
        ),
    )

    generated = questions.generate_question(qtype="behavioral", bucket="experience")
    pasted = questions.custom_question(
        "behavioral", "What is a piece of feedback that changed how you work?"
    )

    assert generated.source == "generated"
    assert generated.fallback_reason is None
    assert pasted.source == "pasted"


def test_legacy_question_sources_are_normalized_conservatively() -> None:
    assert Question(id="user", qtype="behavioral", prompt="q", source="user").source == "pasted"
    assert Question(id="bank", qtype="behavioral", prompt="q", source="bank").source == "mock"
    assert Question(id="followup", qtype="behavioral", prompt="q", source="followup").source == "mock"


def test_health_exposes_llm_and_stt_capabilities(monkeypatch) -> None:
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "azure_openai_whisper_endpoint", "")
    monkeypatch.setattr(settings, "azure_openai_whisper_api_key", "")
    monkeypatch.setattr(settings, "azure_openai_whisper_deployment", "")

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["llm_status"] == "mock"
    assert body["stt_status"] == "mock"
    assert body["mock_mode"] is True
