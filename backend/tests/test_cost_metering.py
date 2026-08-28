"""Billing uses the provider's own token counts, not a guess at them.

The old path estimated tokens as ``len(text.split()) * 1.3``, which cannot see
reasoning tokens. Scoring runs on pro with a 2048-token thinking budget and those
tokens bill at the output rate, so every scorecard was undercounted ~7x. With a
daily cap that actually binds, that is the difference between degrading gracefully
and being cut off upstream with no warning.
"""

from app.config import settings
from app.services.budget import cost_of_call, estimate_gemini_cost
from app.services.llm_client import LLMResult, _sum_opt

PRO = "gemini-2.5-pro"


def test_metered_call_uses_reported_tokens_not_text_length():
    # A tiny JSON response that took 3048 output tokens to produce (2048 of them
    # thinking). Text length says "cheap"; the real usage says otherwise.
    result = LLMResult('{"dimensions":[]}', input_tokens=2000, output_tokens=3048)
    assert cost_of_call(result, "word " * 1500, model=PRO) == estimate_gemini_cost(
        2000, 3048, model=PRO
    )


def test_thinking_tokens_are_billed_as_output():
    # candidates + thoughts, because Gemini bills reasoning at the output rate.
    assert _sum_opt(1000, 2048) == 3048


def test_missing_thinking_count_is_zero_not_unknown():
    # Models without a reasoning pass omit the field; that must not discard the
    # perfectly good candidates count and fall back to guessing.
    assert _sum_opt(1000, None) == 1000


def test_no_reported_usage_falls_back_to_estimate():
    prompt = "word " * 100          # 100 words -> 130 estimated tokens
    response = "some response text"  # 3 words   ->   3 estimated tokens
    cost = cost_of_call(LLMResult(response), prompt, model=PRO)
    assert cost > 0, "an unmetered provider must never bill zero"
    assert cost == estimate_gemini_cost(int(100 * 1.3), int(3 * 1.3), model=PRO)


def test_metering_closes_a_large_undercount_on_a_scoring_call():
    prompt = "word " * 1500
    metered = cost_of_call(LLMResult("{}", 2000, 3048), prompt, model=PRO)
    guessed = cost_of_call(LLMResult("{}"), prompt, model=PRO)
    assert metered > guessed * 3, (metered, guessed)


def test_scoring_completion_returns_a_metered_result(monkeypatch):
    from app.services import scoring

    monkeypatch.setattr(
        scoring, "chat_completion", lambda p, **kw: LLMResult("{}", 11, 22)
    )
    result = scoring._score_completion("prompt")
    assert isinstance(result, LLMResult) and result.metered
    assert (result.input_tokens, result.output_tokens) == (11, 22)


def test_scoring_requests_a_real_thinking_budget():
    # The budget is what makes thinking tokens exist; if it ever silently went to
    # 0 the metering above would still pass but scoring quality would regress.
    assert settings.gemini_scoring_thinking_budget > 0
