"""Mock interview orchestration — a guided multi-question session with follow-ups.

A session is an ordered PLAN of main-question specs plus an append-only TURNS log.
Each turn (main question or dynamic follow-up) is realized as one regular attempt, so
the whole record→transcribe→delivery-metrics→score pipeline is reused unchanged.

All cursors are DERIVED from the turns log (never stored as mutable counters):
- the current turn is the last appended turn;
- follow-ups-asked for a main question = count of follow-up turns sharing its plan_index.
This keeps the in-memory cache and Supabase in sync and makes /advance idempotent.
"""

import random
import uuid
from typing import Optional

from app.models import (
    InterviewMainSpec,
    InterviewReport,
    InterviewReportTurn,
    InterviewSession,
    InterviewTurn,
    Question,
    Scorecard,
)
from app.services import questions, scoring, store
from app.services.auth import Identity
from app.services.behavioral import BUCKET_KEYS

# Per-section follow-up caps (how "deep" the interviewer probes one question).
_CODING_CAP = 2
_HEAVY_CAP = 4  # system design / project — "heavy follow-ups on the one question"
_BEHAVIORAL_CAP = 2

TECHNICAL_SECTIONS = ("coding", "system_design", "project")


# --- plan -------------------------------------------------------------------

def build_plan(
    mode: str, section: Optional[str], num_behavioral: int, identity: Identity
) -> list[InterviewMainSpec]:
    """The immutable ordered list of MAIN questions for the interview."""
    specs: list[InterviewMainSpec] = []
    focus = questions.pick_focus(identity) or {}
    focus_dim = focus.get("dimension")
    if mode == "technical":
        section = section if section in TECHNICAL_SECTIONS else "coding"
        spec_focus = focus_dim if focus.get("track") == section else None
        if section == "coding":
            # 2-3 problems escalating in difficulty.
            for diff in ("easy", "medium", "hard"):
                specs.append(
                    InterviewMainSpec(
                        qtype="technical",
                        track="coding",
                        difficulty=diff,
                        followup_cap=_CODING_CAP,
                        focus=spec_focus,
                    )
                )
        else:
            # system_design / project, one question, heavy follow-ups.
            specs.append(
                InterviewMainSpec(
                    qtype="technical",
                    track=section,
                    followup_cap=_HEAVY_CAP,
                    focus=spec_focus,
                )
            )
    else:
        # Behavioral, spread main questions across the buckets.
        n = max(1, min(5, num_behavioral or 3))
        focus_bucket = focus.get("bucket")
        if focus_bucket in BUCKET_KEYS:
            buckets = [focus_bucket] + [b for b in BUCKET_KEYS if b != focus_bucket]
        else:
            buckets = list(BUCKET_KEYS)
            random.shuffle(buckets)
        for i in range(n):
            bucket = buckets[i % len(buckets)]
            specs.append(
                InterviewMainSpec(
                    qtype="behavioral",
                    bucket=bucket,
                    followup_cap=_BEHAVIORAL_CAP,
                    focus=focus_dim if bucket == focus_bucket else None,
                )
            )
    return specs


# --- turn helpers (cursors derived from the log) ----------------------------

def _new_turn(
    plan_index: int,
    question_id: str,
    is_followup: bool = False,
    parent_turn_id: Optional[str] = None,
) -> InterviewTurn:
    return InterviewTurn(
        turn_id=str(uuid.uuid4()),
        plan_index=plan_index,
        is_followup=is_followup,
        parent_turn_id=parent_turn_id,
        question_id=question_id,
    )


def _main_turn(session: InterviewSession, plan_index: int) -> Optional[InterviewTurn]:
    for t in session.turns:
        if t.plan_index == plan_index and not t.is_followup:
            return t
    return None


def _realize_main(spec: InterviewMainSpec, config: dict, identity: Identity) -> Question:
    q = questions.generate_question(
        qtype=spec.qtype,
        role=config.get("role", "Software Engineer"),
        seniority=config.get("seniority", "mid"),
        difficulty=spec.difficulty,
        track=spec.track,
        bucket=spec.bucket,
        competency=spec.competency,
        focus=spec.focus,
    )
    if spec.focus:
        q.meta["focus"] = spec.focus
    return store.create_question(
        q, owner_user_id=identity.user_id, guest_token=identity.guest_token
    )


def _progress_label(session: InterviewSession, turn: InterviewTurn) -> str:
    if turn.is_followup:
        return "Follow-up"
    main_count = len(session.plan)
    return f"Question {turn.plan_index + 1} of {main_count}"


# --- start ------------------------------------------------------------------

def start_interview(
    mode: str,
    section: Optional[str],
    role: str,
    seniority: str,
    num_behavioral: int,
    identity: Identity,
) -> tuple[InterviewSession, InterviewTurn, Question]:
    plan = build_plan(mode, section, num_behavioral, identity)
    config = {"role": role, "seniority": seniority, "section": section, "mode": mode}
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        mode=mode,
        user_id=identity.user_id,
        guest_token=identity.guest_token,
        config=config,
        plan=plan,
        turns=[],
    )
    q = _realize_main(plan[0], config, identity)
    turn = _new_turn(0, q.id)
    session.turns.append(turn)
    store.create_interview(session)
    return session, turn, q


# --- advance ----------------------------------------------------------------

def decide_next(
    session: InterviewSession,
    turn_id: Optional[str],
    finished_attempt_id: str,
    transcript: str,
    identity: Identity,
) -> tuple[Optional[InterviewTurn], Optional[Question]]:
    """Record the finished answer and return the next turn/question, or (None, None) when done.

    Idempotent: a duplicate /advance for an already-answered turn returns whatever turn
    already follows it instead of double-advancing.
    """
    if not session.turns:
        return None, None

    turn = next((t for t in session.turns if t.turn_id == turn_id), None) if turn_id else None
    if turn is None:
        turn = session.turns[-1]

    if turn.answered:
        # Duplicate call, return the already-created next turn (if any).
        idx = session.turns.index(turn)
        if idx + 1 < len(session.turns):
            nxt = session.turns[idx + 1]
            return nxt, store.get_question(nxt.question_id)
        return None, None

    turn.attempt_id = finished_attempt_id
    turn.answered = True

    spec = session.plan[turn.plan_index]
    followups_done = sum(
        1 for t in session.turns if t.plan_index == turn.plan_index and t.is_followup
    )

    next_turn: Optional[InterviewTurn] = None
    next_q: Optional[Question] = None

    # Try a dynamic follow-up that probes the answer they just gave.
    if followups_done < spec.followup_cap:
        answered_q = store.get_question(turn.question_id)
        prior = [
            (store.get_question(t.question_id).prompt if store.get_question(t.question_id) else "")
            for t in session.turns
            if t.plan_index == turn.plan_index and t.is_followup
        ]
        fu = None
        if answered_q is not None:
            fu = questions.generate_followup(
                answered_q, transcript, [p for p in prior if p],
                seniority=session.config.get("seniority", "mid"),
            )
        if fu is not None:
            store.create_question(
                fu, owner_user_id=identity.user_id, guest_token=identity.guest_token
            )
            parent = _main_turn(session, turn.plan_index)
            next_turn = _new_turn(
                turn.plan_index, fu.id, is_followup=True,
                parent_turn_id=parent.turn_id if parent else turn.turn_id,
            )
            session.turns.append(next_turn)
            next_q = fu

    # No follow-up → move to the next main question (or finish).
    if next_q is None:
        next_index = turn.plan_index + 1
        if next_index < len(session.plan):
            # Use the background-prefetched question if it's ready; else generate now.
            pre_id = session.prefetched.get(next_index)
            next_q = store.get_question(pre_id) if pre_id else None
            if next_q is None:
                next_q = _realize_main(session.plan[next_index], session.config, identity)
            next_turn = _new_turn(next_index, next_q.id)
            session.turns.append(next_turn)

    store.update_interview(session)
    return next_turn, next_q


def prefetch_main(session: InterviewSession, plan_index: int, identity: Identity) -> None:
    """Generate the main question at ``plan_index`` ahead of time (background task).

    Idempotent and best-effort: skips indices out of range, already realized as a turn,
    or already prefetched, and swallows any error so a failed prefetch just falls back to
    on-demand generation in ``decide_next``. Runs after the response is sent, during the
    candidate's answer window, so main-question transitions don't wait on the LLM.
    """
    try:
        if plan_index < 0 or plan_index >= len(session.plan):
            return
        if plan_index in session.prefetched:
            return
        if _main_turn(session, plan_index) is not None:
            return
        q = _realize_main(session.plan[plan_index], session.config, identity)
        session.prefetched[plan_index] = q.id
        store.update_interview(session)
    except Exception:
        pass


def pending_turn(session: InterviewSession) -> Optional[InterviewTurn]:
    """The current unanswered turn (for resume), if any."""
    for t in reversed(session.turns):
        if not t.answered:
            return t
    return None


# --- final report -----------------------------------------------------------

def build_report(session: InterviewSession, identity: Identity) -> InterviewReport:
    """Lead with ONE generalized rubric for the whole interview (behavioral vs technical);
    per-question scorecards are fetched on demand via each turn's attempt. Aggregates
    delivery across all answers."""
    if session.report is not None:
        return session.report

    # Gather answered turns + their attempt/question once.
    answered: list[tuple] = []
    for t in session.turns:
        if not t.answered or not t.attempt_id:
            continue
        attempt = store.get_attempt(t.attempt_id, identity)
        question = store.get_question(t.question_id)
        if attempt is None or question is None:
            continue
        answered.append((t, attempt, question))

    total_fillers = 0
    total_pauses = 0
    wpms: list[float] = []
    qa_lines: list[str] = []
    report_turns: list[InterviewReportTurn] = []

    for t, attempt, question in answered:
        m = attempt.metrics
        total_fillers += m.total_fillers
        total_pauses += m.total_pauses
        if m.words_per_minute:
            wpms.append(m.words_per_minute)
        transcript = (attempt.transcript_text or " ".join(w.word for w in attempt.words)).strip()
        tag = "Follow-up" if t.is_followup else "Question"
        qa_lines.append(f"[{tag}] {question.prompt}\nAnswer: {transcript or '(no answer)'}")
        # Light turn, no per-question scorecard up front; attempt_id lets us fetch it later.
        report_turns.append(
            InterviewReportTurn(
                turn_id=t.turn_id,
                question=question.prompt,
                is_followup=t.is_followup,
                attempt_id=t.attempt_id,
            )
        )

    avg_wpm = round(sum(wpms) / len(wpms), 1) if wpms else 0.0
    delivery = (
        f"{avg_wpm} words/min, {total_fillers} filler words, {total_pauses} pauses across the interview"
    )
    qa_block = "\n\n".join(qa_lines)
    mode = "technical" if session.mode == "technical" else "behavioral"
    seniority = session.config.get("seniority", "")

    general_card = None
    overall = 0.0
    verdict = summary = followup_handling = ""
    strengths: list[str] = []
    improvements: list[str] = []
    if qa_block:
        try:
            g = scoring.score_interview(qa_block, delivery, mode, seniority)
            general_card = Scorecard(
                attempt_id=session.session_id,
                rubric=g["rubric"],
                overall_score=g["overall_score"],
                overall_summary=g["overall_summary"],
                dimensions=g["dimensions"],
            )
            overall = g["overall_score"]
            verdict = g["verdict"] or _verdict_from_score(overall)
            summary = g["overall_summary"]
            strengths = g["strengths"]
            improvements = g["improvements"]
            followup_handling = g["followup_handling"]
        except Exception:
            verdict = _verdict_from_score(overall)

    report = InterviewReport(
        overall_score=overall,
        verdict=verdict,
        summary=summary,
        strengths=strengths,
        improvements=improvements,
        followup_handling=followup_handling,
        general_scorecard=general_card,
        total_fillers=total_fillers,
        avg_words_per_minute=avg_wpm,
        total_pauses=total_pauses,
        turns=report_turns,
    )
    session.report = report
    session.status = "complete"
    store.update_interview(session)
    return report


def _verdict_from_score(score: float) -> str:
    if score >= 4.0:
        return "strong"
    if score >= 2.8:
        return "mixed"
    return "needs work"
