"""Attempt persistence facade.

Two layers:
- `session_store` (in-memory) is the fast live cache the analysis pipeline writes
  to during streaming.
- Supabase is the durable store (attempts + delivery_metrics + fillers +
  transcript_words), written at creation and on completion, and read for history.

Every read/write is scoped to the caller's `Identity` (signed-in user or guest token)
so users can only ever touch their own attempts. When Supabase is unconfigured
(local/demo dev) everything runs against the in-memory cache only.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import (
    AttemptSummary,
    DimensionScore,
    FillerOccurrence,
    InterviewMainSpec,
    InterviewReport,
    InterviewSession,
    InterviewTurn,
    Profile,
    Question,
    QuestionExample,
    Scorecard,
    ScoreDimension,
    SessionMetrics,
    SessionResult,
    SessionStatus,
    WordTimestamp,
    answer_cap_sec,
)
from app.services import session_store, storage, supabase_client
from app.services.auth import Identity
from app.services.bounded_cache import BoundedCache

# Process-local caches. Bounded (LRU) because the backend is a long-lived single
# worker: unbounded, these grew for the life of the process. With Supabase configured
# an eviction just costs a re-read; without it (local/demo) the entry is gone, so the
# bounds sit far above any realistic single-session working set.
_mem_questions: BoundedCache[str, Question] = BoundedCache(2000)
_mem_scorecards: BoundedCache[str, Scorecard] = BoundedCache(1000)
_mem_interviews: BoundedCache[str, InterviewSession] = BoundedCache(500)
_mem_profiles: BoundedCache[str, Profile] = BoundedCache(1000)


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
    q = get_question(question_id) if question_id else None
    track = (q.meta or {}).get("track") if q else None
    cap = answer_cap_sec(q.qtype if q else None, track)
    session = SessionResult(
        session_id=attempt_id,
        status=SessionStatus.PENDING,
        title=title,
        user_id=identity.user_id,
        guest_token=identity.guest_token,
        question_id=question_id,
        created_at=_now_iso(),
        max_duration_sec=cap,
    )
    session_store.update_session(session)  # seed live cache

    if supabase_client.is_configured():
        payload = {
            "id": attempt_id,
            "user_id": identity.user_id,
            "guest_token": identity.guest_token,
            "question_id": question_id,
            "title": title,
            "status": SessionStatus.PENDING.value,
            "max_duration_sec": cap,
        }
        try:
            supabase_client.get_client().table("attempts").insert(payload).execute()
        except Exception:
            payload.pop("max_duration_sec", None)
            try:
                supabase_client.get_client().table("attempts").insert(payload).execute()
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


def _rel_first(value) -> dict:
    if isinstance(value, list):
        return value[0] if value else {}
    return value or {}


def _dim_scores(raw) -> list[DimensionScore]:
    out: list[DimensionScore] = []
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        name = item.get("dimension")
        if not name:
            continue
        try:
            score = float(item.get("score") or 0)
        except (TypeError, ValueError):
            score = 0.0
        out.append(DimensionScore(dimension=str(name), score=score))
    return out


def _bucket_of(qtype: Optional[str], meta: Optional[dict]) -> Optional[str]:
    meta = meta or {}
    return meta.get("bucket") or meta.get("track") or qtype


def _summary_from_session(s: SessionResult) -> AttemptSummary:
    sc = _mem_scorecards.get(s.session_id)
    q = _mem_questions.get(s.question_id) if s.question_id else None
    meta = dict(q.meta) if q else {}
    dims = _dim_scores([d.model_dump() for d in sc.dimensions]) if sc else []
    return AttemptSummary(
        session_id=s.session_id,
        title=s.title,
        status=s.status,
        created_at=s.created_at,
        total_fillers=s.metrics.total_fillers,
        duration_sec=s.metrics.duration_sec,
        fillers_per_minute=s.metrics.fillers_per_minute,
        words_per_minute=s.metrics.words_per_minute,
        overall_score=sc.overall_score if sc else None,
        dimensions=dims,
        bucket=_bucket_of(q.qtype if q else None, meta),
        qtype=q.qtype if q else None,
        rubric=sc.rubric if sc else None,
    )


def list_attempts(identity: Identity) -> list[AttemptSummary]:
    if not supabase_client.is_configured():
        out = [
            _summary_from_session(s)
            for s in session_store.list_sessions()
            if _owns(s, identity)
        ]
        return sorted(out, key=lambda a: a.created_at or "", reverse=True)

    try:
        client = supabase_client.get_client()
        q = client.table("attempts").select(
            "id,title,status,created_at,duration_sec,"
            "delivery_metrics(total_fillers,fillers_per_minute,words_per_minute),"
            "scorecards(overall_score,dimensions,rubric),"
            "questions(qtype,meta)"
        )
        if identity.user_id:
            q = q.eq("user_id", identity.user_id)
        else:
            q = q.eq("guest_token", identity.guest_token or "")
        rows = q.order("created_at", desc=True).execute().data or []
        summaries = []
        for row in rows:
            dm = _rel_first(row.get("delivery_metrics"))
            sc = _rel_first(row.get("scorecards"))
            qn = _rel_first(row.get("questions"))
            overall = sc.get("overall_score")
            summaries.append(
                AttemptSummary(
                    session_id=row["id"],
                    title=row.get("title") or "Untitled Attempt",
                    status=row.get("status", "pending"),
                    created_at=row.get("created_at"),
                    total_fillers=dm.get("total_fillers", 0) or 0,
                    duration_sec=row.get("duration_sec") or 0.0,
                    fillers_per_minute=dm.get("fillers_per_minute", 0.0) or 0.0,
                    words_per_minute=dm.get("words_per_minute", 0.0) or 0.0,
                    overall_score=float(overall) if overall is not None else None,
                    dimensions=_dim_scores(sc.get("dimensions")),
                    bucket=_bucket_of(qn.get("qtype"), qn.get("meta") if isinstance(qn.get("meta"), dict) else {}),
                    qtype=qn.get("qtype"),
                    rubric=sc.get("rubric"),
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
        update = (
            client.table("attempts")
            .update(
                {
                    "title": session.title,
                    "status": session.status.value,
                    "transcript_text": session.transcript_text,
                    "duration_sec": session.metrics.duration_sec,
                    "audio_path": session.audio_path,
                    "updated_at": _now_iso(),
                }
            )
            .eq("id", session.session_id)
        )
        if session.user_id:
            update = update.eq("user_id", session.user_id)
        else:
            update = update.eq("guest_token", session.guest_token)
        update.execute()

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

def create_question(
    question: Question,
    owner_user_id: Optional[str] = None,
    guest_token: Optional[str] = None,
) -> Question:
    question.created_at = question.created_at or _now_iso()
    question.owner_user_id = owner_user_id
    if guest_token and not owner_user_id:
        question.meta = dict(question.meta or {})
        question.meta["_guest_token"] = guest_token
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
            owner_user_id=r.get("owner_user_id"),
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
    audio_path = row.get("audio_path") or None
    return SessionResult(
        session_id=row["id"],
        status=row.get("status", "complete"),
        title=row.get("title") or "Untitled Attempt",
        user_id=row.get("user_id"),
        guest_token=row.get("guest_token"),
        question_id=row.get("question_id"),
        transcript_text=row.get("transcript_text") or "",
        audio_path=audio_path,
        audio_url=storage.audio_url(audio_path),
        created_at=row.get("created_at"),
        max_duration_sec=row.get("max_duration_sec"),
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
        "clip_path": storage.clip_key(f.clip_url),
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
        clip_url=storage.clip_url(row.get("clip_path")),
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


# --- profiles ---------------------------------------------------------------

def get_profile(user_id: str) -> Optional[Profile]:
    if user_id in _mem_profiles:
        return _mem_profiles[user_id]
    if not supabase_client.is_configured():
        return None
    try:
        rows = (
            supabase_client.get_client()
            .table("profiles")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
            .data
        )
        if not rows:
            return None
        r = rows[0]
        return Profile(
            user_id=r["user_id"],
            target_role=r.get("target_role") or "Software Engineer",
            seniority=r.get("seniority") or "mid",
        )
    except Exception:
        return None


def upsert_profile(user_id: str, target_role: Optional[str] = None, seniority: Optional[str] = None) -> Profile:
    existing = get_profile(user_id)
    profile = Profile(
        user_id=user_id,
        target_role=target_role or (existing.target_role if existing else "Software Engineer"),
        seniority=seniority or (existing.seniority if existing else "mid"),
    )
    _mem_profiles[user_id] = profile
    if supabase_client.is_configured():
        try:
            supabase_client.get_client().table("profiles").upsert(
                {
                    "user_id": user_id,
                    "target_role": profile.target_role,
                    "seniority": profile.seniority,
                    "updated_at": _now_iso(),
                }
            ).execute()
        except Exception:
            pass
    return profile
