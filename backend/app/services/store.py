"""Attempt persistence facade.

Two layers:
- `session_store` (in-memory) is the fast live cache the analysis pipeline writes
  to during streaming.
- Supabase is the durable store (attempts + delivery_metrics + fillers +
  transcript_words), written at creation and on completion, and read for history.

Every read/write is scoped to the caller's `Identity` (Clerk user or guest token)
so users can only ever touch their own attempts. When Supabase is unconfigured
(local/demo dev) everything runs against the in-memory cache only.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import (
    AttemptSummary,
    FillerOccurrence,
    InterviewMainSpec,
    InterviewReport,
    InterviewSession,
    InterviewTurn,
    Question,
    QuestionExample,
    Scorecard,
    ScoreDimension,
    SessionMetrics,
    SessionResult,
    SessionStatus,
    WordTimestamp,
)
from app.services import session_store, supabase_client
from app.services.auth import Identity

# In-memory fallbacks (used when Supabase is unconfigured)
_mem_questions: dict[str, Question] = {}
_mem_scorecards: dict[str, Scorecard] = {}
_mem_interviews: dict[str, InterviewSession] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _owns(session: SessionResult, identity: Identity) -> bool:
    if identity.user_id and session.user_id == identity.user_id:
        return True
    if identity.guest_token and session.guest_token == identity.guest_token:
        return True
    return False


# --- create -----------------------------------------------------------------

def create_attempt(
    identity: Identity, title: str = "Untitled Attempt", question_id: Optional[str] = None
) -> SessionResult:
    attempt_id = str(uuid.uuid4())
    session = SessionResult(
        session_id=attempt_id,
        status=SessionStatus.PENDING,
        title=title,
        user_id=identity.user_id,
        guest_token=identity.guest_token,
        question_id=question_id,
        created_at=_now_iso(),
    )
    session_store.update_session(session)  # seed live cache

    if supabase_client.is_configured():
        try:
            supabase_client.get_client().table("attempts").insert(
                {
                    "id": attempt_id,
                    "user_id": identity.user_id,
                    "guest_token": identity.guest_token,
                    "question_id": question_id,
                    "title": title,
                    "status": SessionStatus.PENDING.value,
                }
            ).execute()
        except Exception:
            pass

    return session


# --- read -------------------------------------------------------------------

def get_attempt(attempt_id: str, identity: Identity) -> Optional[SessionResult]:
    cached = session_store.get_session(attempt_id)
    if cached is not None:
        return cached if _owns(cached, identity) else None

    if not supabase_client.is_configured():
        return None

    try:
        client = supabase_client.get_client()
        rows = client.table("attempts").select("*").eq("id", attempt_id).limit(1).execute().data
        if not rows:
            return None
        row = rows[0]
        session = _row_to_session(row)
        if not _owns(session, identity):
            return None
        _hydrate_children(client, session)
        return session
    except Exception:
        return None


def list_attempts(identity: Identity) -> list[AttemptSummary]:
    if not supabase_client.is_configured():
        out = []
        for s in session_store.list_sessions():
            if _owns(s, identity):
                out.append(
                    AttemptSummary(
                        session_id=s.session_id,
                        title=s.title,
                        status=s.status,
                        created_at=s.created_at,
                        total_fillers=s.metrics.total_fillers,
                        duration_sec=s.metrics.duration_sec,
                    )
                )
        return sorted(out, key=lambda a: a.created_at or "", reverse=True)

    try:
        client = supabase_client.get_client()
        q = client.table("attempts").select(
            "id,title,status,created_at,duration_sec,delivery_metrics(total_fillers)"
        )
        if identity.user_id:
            q = q.eq("user_id", identity.user_id)
        else:
            q = q.eq("guest_token", identity.guest_token or "")
        rows = q.order("created_at", desc=True).execute().data or []
        summaries = []
        for row in rows:
            dm = row.get("delivery_metrics") or {}
            if isinstance(dm, list):
                dm = dm[0] if dm else {}
            summaries.append(
                AttemptSummary(
                    session_id=row["id"],
                    title=row.get("title") or "Untitled Attempt",
                    status=row.get("status", "pending"),
                    created_at=row.get("created_at"),
                    total_fillers=(dm or {}).get("total_fillers", 0) or 0,
                    duration_sec=row.get("duration_sec") or 0.0,
                )
            )
        return summaries
    except Exception:
        return []


# --- persist results --------------------------------------------------------

def persist_attempt_results(session: SessionResult) -> None:
    """Write durable rows for a finished (or failed) attempt. No-op without Supabase."""
    if not supabase_client.is_configured():
        return
    try:
        client = supabase_client.get_client()
        client.table("attempts").update(
            {
                "title": session.title,
                "status": session.status.value,
                "transcript_text": session.transcript_text,
                "duration_sec": session.metrics.duration_sec,
                "audio_path": session.audio_url and session.audio_url.split("/")[-1],
                "updated_at": _now_iso(),
            }
        ).eq("id", session.session_id).execute()

        if session.status == SessionStatus.COMPLETE:
            metrics_row = {
                "attempt_id": session.session_id,
                **_metrics_to_row(session.metrics),
                # Pauses come from audio silence detection and can't be recomputed
                # from word timestamps, so store the list alongside the metrics.
                "pauses": [p.model_dump() for p in session.pauses],
            }
            try:
                client.table("delivery_metrics").upsert(metrics_row).execute()
            except Exception:
                # The `pauses` column may not exist yet (migration not applied). Don't
                # let that drop the rest of the metrics, retry without it.
                metrics_row.pop("pauses", None)
                client.table("delivery_metrics").upsert(metrics_row).execute()
            # Replace child rows
            client.table("fillers").delete().eq("attempt_id", session.session_id).execute()
            client.table("transcript_words").delete().eq("attempt_id", session.session_id).execute()
            if session.fillers:
                client.table("fillers").insert(
                    [_filler_to_row(session.session_id, f) for f in session.fillers]
                ).execute()
            if session.words:
                client.table("transcript_words").insert(
                    [_word_to_row(session.session_id, w) for w in session.words]
                ).execute()
    except Exception:
        # Persistence failures must not break the user-facing analysis flow.
        pass


# --- questions --------------------------------------------------------------

def create_question(question: Question, owner_user_id: Optional[str] = None) -> Question:
    question.created_at = question.created_at or _now_iso()
    _mem_questions[question.id] = question
    if supabase_client.is_configured():
        try:
            # Fold constraints/examples into meta (no dedicated columns yet)
            meta = dict(question.meta)
            meta["_constraints"] = question.constraints
            meta["_examples"] = [e.model_dump() for e in question.examples]
            supabase_client.get_client().table("questions").insert(
                {
                    "id": question.id,
                    "owner_user_id": owner_user_id,
                    "qtype": question.qtype,
                    "prompt": question.prompt,
                    "source": question.source,
                    "meta": meta,
                }
            ).execute()
        except Exception:
            pass
    return question


def get_question(question_id: str) -> Optional[Question]:
    if question_id in _mem_questions:
        return _mem_questions[question_id]
    if not supabase_client.is_configured():
        return None
    try:
        rows = (
            supabase_client.get_client()
            .table("questions")
            .select("*")
            .eq("id", question_id)
            .limit(1)
            .execute()
            .data
        )
        if not rows:
            return None
        r = rows[0]
        meta = dict(r.get("meta") or {})
        constraints = meta.pop("_constraints", None)
        examples = [QuestionExample(**e) for e in (meta.pop("_examples", []) or [])]
        return Question(
            id=r["id"],
            qtype=r["qtype"],
            prompt=r["prompt"],
            source=r.get("source", "generated"),
            constraints=constraints,
            examples=examples,
            meta=meta,
            created_at=r.get("created_at"),
        )
    except Exception:
        return None


# --- scorecards -------------------------------------------------------------

def save_scorecard(scorecard: Scorecard) -> Scorecard:
    scorecard.created_at = scorecard.created_at or _now_iso()
    _mem_scorecards[scorecard.attempt_id] = scorecard
    if supabase_client.is_configured():
        try:
            client = supabase_client.get_client()
            client.table("scorecards").delete().eq("attempt_id", scorecard.attempt_id).execute()
            client.table("scorecards").insert(
                {
                    "attempt_id": scorecard.attempt_id,
                    "rubric": scorecard.rubric,
                    "overall_score": scorecard.overall_score,
                    "overall_summary": scorecard.overall_summary,
                    "dimensions": [d.model_dump() for d in scorecard.dimensions],
                }
            ).execute()
        except Exception:
            pass
    return scorecard


def get_scorecard(attempt_id: str) -> Optional[Scorecard]:
    if attempt_id in _mem_scorecards:
        return _mem_scorecards[attempt_id]
    if not supabase_client.is_configured():
        return None
    try:
        rows = (
            supabase_client.get_client()
            .table("scorecards")
            .select("*")
            .eq("attempt_id", attempt_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )
        if not rows:
            return None
        r = rows[0]
        return Scorecard(
            attempt_id=r["attempt_id"],
            rubric=r["rubric"],
            overall_score=r.get("overall_score") or 0.0,
            overall_summary=r.get("overall_summary") or "",
            dimensions=[ScoreDimension(**d) for d in (r.get("dimensions") or [])],
            created_at=r.get("created_at"),
        )
    except Exception:
        return None


# --- row mappers ------------------------------------------------------------

def _row_to_session(row: dict) -> SessionResult:
    return SessionResult(
        session_id=row["id"],
        status=row.get("status", "complete"),
        title=row.get("title") or "Untitled Attempt",
        user_id=row.get("user_id"),
        guest_token=row.get("guest_token"),
        question_id=row.get("question_id"),
        transcript_text=row.get("transcript_text") or "",
        created_at=row.get("created_at"),
    )


def _hydrate_children(client, session: SessionResult) -> None:
    aid = session.session_id
    from app.models import PauseOccurrence

    metrics = client.table("delivery_metrics").select("*").eq("attempt_id", aid).execute().data
    if metrics:
        session.metrics = _row_to_metrics(metrics[0])
        session.pauses = [
            PauseOccurrence(**p) for p in (metrics[0].get("pauses") or [])
        ]
    words = (
        client.table("transcript_words").select("*").eq("attempt_id", aid).order("word_index").execute().data
        or []
    )
    session.words = [
        WordTimestamp(word=w["word"], start=w["start_time"], end=w["end_time"], index=w["word_index"])
        for w in words
    ]
    fillers = client.table("fillers").select("*").eq("attempt_id", aid).order("word_index").execute().data or []
    session.fillers = [_row_to_filler(f) for f in fillers]


def _metrics_to_row(m: SessionMetrics) -> dict:
    return {
        "total_fillers": m.total_fillers,
        "fillers_per_minute": m.fillers_per_minute,
        "words_per_minute": m.words_per_minute,
        "avg_pause_sec": m.avg_pause_sec,
        "avg_pause_before_filler_sec": m.avg_pause_before_filler_sec,
        "avg_pause_elsewhere_sec": m.avg_pause_elsewhere_sec,
        "total_pauses": m.total_pauses,
        "long_pauses": m.long_pauses,
        "pauses_per_minute": m.pauses_per_minute,
        "total_pause_sec": m.total_pause_sec,
        "long_pause_filler_pct": m.long_pause_filler_pct,
        "transition_filler_pct": m.transition_filler_pct,
        "position_breakdown": m.position_breakdown.model_dump(),
        "filler_breakdown": m.filler_breakdown,
        "tag_breakdown": m.tag_breakdown,
    }


def _row_to_metrics(row: dict) -> SessionMetrics:
    from app.models import PositionBreakdown

    return SessionMetrics(
        duration_sec=row.get("duration_sec", 0.0) or 0.0,
        total_fillers=row.get("total_fillers", 0) or 0,
        fillers_per_minute=row.get("fillers_per_minute", 0.0) or 0.0,
        words_per_minute=row.get("words_per_minute", 0.0) or 0.0,
        avg_pause_sec=row.get("avg_pause_sec", 0.0) or 0.0,
        avg_pause_before_filler_sec=row.get("avg_pause_before_filler_sec", 0.0) or 0.0,
        avg_pause_elsewhere_sec=row.get("avg_pause_elsewhere_sec", 0.0) or 0.0,
        total_pauses=row.get("total_pauses", 0) or 0,
        long_pauses=row.get("long_pauses", 0) or 0,
        pauses_per_minute=row.get("pauses_per_minute", 0.0) or 0.0,
        total_pause_sec=row.get("total_pause_sec", 0.0) or 0.0,
        long_pause_filler_pct=row.get("long_pause_filler_pct", 0.0) or 0.0,
        transition_filler_pct=row.get("transition_filler_pct", 0.0) or 0.0,
        position_breakdown=PositionBreakdown(**(row.get("position_breakdown") or {})),
        filler_breakdown=row.get("filler_breakdown") or {},
        tag_breakdown=row.get("tag_breakdown") or {},
    )


def _filler_to_row(attempt_id: str, f: FillerOccurrence) -> dict:
    return {
        "attempt_id": attempt_id,
        "word": f.word,
        "start_time": f.start,
        "end_time": f.end,
        "word_index": f.index,
        "context_text": f.context,
        "clip_path": f.clip_url,
        "sentence_position": f.sentence_position,
        "is_transition_related": f.is_transition_related,
        "tag": f.tag,
        "tag_reason": f.tag_reason,
        "topic": f.topic,
    }


def _row_to_filler(row: dict) -> FillerOccurrence:
    return FillerOccurrence(
        word=row["word"],
        start=row["start_time"],
        end=row["end_time"],
        index=row["word_index"],
        context=row.get("context_text") or "",
        sentence_position=row.get("sentence_position") or "middle",
        is_transition_related=row.get("is_transition_related") or False,
        tag=row.get("tag"),
        tag_reason=row.get("tag_reason"),
        topic=row.get("topic"),
        clip_url=row.get("clip_path"),
    )


def _word_to_row(attempt_id: str, w: WordTimestamp) -> dict:
    return {
        "attempt_id": attempt_id,
        "word": w.word,
        "start_time": w.start,
        "end_time": w.end,
        "word_index": w.index,
    }


# --- mock interviews --------------------------------------------------------
# A multi-question interview session groups many attempts. The heavy per-turn data
# (transcript, metrics, scorecard) lives in the attempts/scorecards tables; the
# session row only stores the plan + the append-only turns log (pointer triples).

def _owns_interview(s: InterviewSession, identity: Identity) -> bool:
    if identity.user_id and s.user_id == identity.user_id:
        return True
    if identity.guest_token and s.guest_token == identity.guest_token:
        return True
    return False


def create_interview(session: InterviewSession) -> InterviewSession:
    session.created_at = session.created_at or _now_iso()
    session.updated_at = _now_iso()
    _mem_interviews[session.session_id] = session
    if supabase_client.is_configured():
        try:
            supabase_client.get_client().table("interview_sessions").insert(
                _interview_to_row(session)
            ).execute()
        except Exception:
            pass
    return session


def update_interview(session: InterviewSession) -> InterviewSession:
    session.updated_at = _now_iso()
    _mem_interviews[session.session_id] = session
    if supabase_client.is_configured():
        try:
            supabase_client.get_client().table("interview_sessions").update(
                _interview_to_row(session, include_id=False)
            ).eq("id", session.session_id).execute()
        except Exception:
            pass
    return session


def get_interview(interview_id: str, identity: Identity) -> Optional[InterviewSession]:
    cached = _mem_interviews.get(interview_id)
    if cached is not None:
        return cached if _owns_interview(cached, identity) else None
    if not supabase_client.is_configured():
        return None
    try:
        rows = (
            supabase_client.get_client()
            .table("interview_sessions")
            .select("*")
            .eq("id", interview_id)
            .limit(1)
            .execute()
            .data
        )
        if not rows:
            return None
        s = _row_to_interview(rows[0])
        if not _owns_interview(s, identity):
            return None
        _mem_interviews[interview_id] = s  # warm the cache for subsequent /advance calls
        return s
    except Exception:
        return None


def list_interviews(identity: Identity) -> list[InterviewSession]:
    if not supabase_client.is_configured():
        out = [s for s in _mem_interviews.values() if _owns_interview(s, identity)]
        return sorted(out, key=lambda s: s.created_at or "", reverse=True)
    try:
        client = supabase_client.get_client()
        q = client.table("interview_sessions").select("*")
        if identity.user_id:
            q = q.eq("user_id", identity.user_id)
        else:
            q = q.eq("guest_token", identity.guest_token or "")
        rows = q.order("created_at", desc=True).execute().data or []
        return [_row_to_interview(r) for r in rows]
    except Exception:
        return []


def _interview_to_row(s: InterviewSession, include_id: bool = True) -> dict:
    row = {
        "user_id": s.user_id,
        "guest_token": s.guest_token,
        "mode": s.mode,
        "status": s.status,
        "config": s.config,
        "plan": [spec.model_dump() for spec in s.plan],
        "turns": [t.model_dump() for t in s.turns],
        "report": s.report.model_dump() if s.report else None,
        "updated_at": s.updated_at,
    }
    if include_id:
        row["id"] = s.session_id
        row["created_at"] = s.created_at
    return row


def _row_to_interview(row: dict) -> InterviewSession:
    return InterviewSession(
        session_id=row["id"],
        status=row.get("status") or "active",
        mode=row.get("mode") or "behavioral",
        user_id=row.get("user_id"),
        guest_token=row.get("guest_token"),
        config=row.get("config") or {},
        plan=[InterviewMainSpec(**p) for p in (row.get("plan") or [])],
        turns=[InterviewTurn(**t) for t in (row.get("turns") or [])],
        report=InterviewReport(**row["report"]) if row.get("report") else None,
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )
