import asyncio
import json
import logging
import shutil
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.models import (
    AdvanceInterviewRequest,
    AttemptSummary,
    BudgetStatus,
    CustomQuestionRequest,
    GenerateQuestionRequest,
    InterviewQuestionResponse,
    InterviewReport,
    InterviewSession,
    ModelAnswer,
    Profile,
    ProfileUpdate,
    Question,
    Scorecard,
    ScoreRequest,
    SessionResult,
    StartInterviewRequest,
)
from app.services import guests, interview, questions, session_store, storage, store
from app.services.auth import (
    Identity,
    auth_configured,
    get_current_user,
    get_optional_identity,
)
from app.services.budget import BudgetExceededError, get_budget_status
from app.services.llm_client import get_provider_label, is_configured
from app.services.pipeline import run_analysis_pipeline
from app.services.ratelimit import expensive_key, limiter
from app.services.scoring import ScoringUnavailable, model_answer, score_attempt
from app.services.supabase_client import is_configured as supabase_configured

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".webm", ".ogg", ".mp4"}
# A capped (1:30) answer is ~1 MB of opus/webm; 25 MB is generous headroom for other
# codecs while blocking disk-fill abuse. Over-long *duration* is rejected later in the
# pipeline (before any paid transcription); this only bounds raw upload size.
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


# --- meta -------------------------------------------------------------------

@router.get("/health")
async def health():
    gemini_ok = is_configured()
    whisper_ok = settings.whisper_configured
    budget = get_budget_status()
    llm_status = "mock" if not gemini_ok else "degraded" if budget.budget_exceeded else "live"
    if whisper_ok:
        transcription_provider = "whisper"
    elif gemini_ok:
        transcription_provider = get_provider_label()
    else:
        transcription_provider = "mock"
    return {
        "status": "ok",
        "llm_status": llm_status,
        "stt_status": "live" if settings.transcription_configured else "mock",
        "gemini_configured": gemini_ok,
        "whisper_configured": whisper_ok,
        "transcription_configured": settings.transcription_configured,
        "mock_mode": not settings.transcription_configured,
        "transcription_provider": transcription_provider,
        "llm_model": settings.gemini_model,
        "scoring_model": settings.effective_scoring_model,
        "whisper_deployment": settings.azure_openai_whisper_deployment or None,
        "rag_enabled": settings.rag_enabled,
        "rerank_enabled": settings.rerank_enabled,
        "ffmpeg_available": bool(shutil.which("ffmpeg")),
        "google_gemini_base_url": settings.google_gemini_base_url or None,
        "auth_configured": auth_configured(),
        "supabase_configured": supabase_configured(),
    }


@router.get("/me")
async def me(identity: Identity = Depends(get_optional_identity)):
    if not identity.is_user:
        return {
            "authenticated": False,
            "user_id": None,
            "auth_configured": auth_configured(),
            "profile": None,
        }
    profile = store.get_profile(identity.user_id) or store.upsert_profile(identity.user_id)
    data = profile.model_dump()
    data["email"] = identity.email
    return {
        "authenticated": True,
        "user_id": identity.user_id,
        "auth_configured": auth_configured(),
        "profile": data,
    }


@router.put("/me", response_model=Profile)
async def update_me(
    body: ProfileUpdate,
    identity: Identity = Depends(get_optional_identity),
):
    if not identity.is_user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return store.upsert_profile(
        identity.user_id,
        target_role=body.target_role,
        seniority=body.seniority,
    )


@router.get("/budget", response_model=BudgetStatus)
async def budget_status():
    return get_budget_status()


# --- questions --------------------------------------------------------------

@router.post("/questions/generate", response_model=Question)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def generate_interview_question(
    request: Request,
    body: GenerateQuestionRequest,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    focus = questions.pick_focus(identity) or {}
    q = questions.generate_question(
        qtype=body.qtype,
        role=body.role,
        seniority=body.seniority,
        difficulty=body.difficulty,
        topic=body.topic,
        track=body.track,
        bucket=focus.get("bucket") if body.qtype != "technical" else None,
        competency=focus.get("competency") if body.qtype != "technical" else None,
        focus=focus.get("dimension"),
    )
    if focus.get("dimension"):
        q.meta["focus"] = focus["dimension"]
    return store.create_question(
        q, owner_user_id=identity.user_id, guest_token=identity.guest_token
    )


@router.post("/questions", response_model=Question)
async def submit_custom_question(
    request: Request,
    body: CustomQuestionRequest,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="Question prompt is required.")
    q = questions.custom_question(body.qtype, body.prompt, body.meta)
    return store.create_question(
        q, owner_user_id=identity.user_id, guest_token=identity.guest_token
    )


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: str, identity: Identity = Depends(get_optional_identity)):
    _require_identity(identity)
    q = store.get_question(question_id)
    if not q or not _can_read_question(q, identity):
        raise HTTPException(status_code=404, detail="Question not found")
    return q


# --- attempts ---------------------------------------------------------------

def _require_identity(identity: Identity) -> None:
    if not identity.is_user and not identity.is_guest:
        raise HTTPException(
            status_code=400,
            detail="Missing identity. Sign in or send an X-Guest-Token header.",
        )


def _can_read_question(question: Question, identity: Identity) -> bool:
    """Bank/global questions (no owner) are readable by any identified caller.
    User-owned rows require that user. Guest-stamped rows require that guest.
    """
    if question.owner_user_id:
        return question.owner_user_id == identity.user_id
    guest_owner = (question.meta or {}).get("_guest_token")
    if guest_owner:
        return guest_owner == identity.guest_token
    return True


@router.post("/attempts", response_model=SessionResult)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def create_attempt(
    request: Request,
    title: str = "Untitled Attempt",
    question_id: str | None = None,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    # Guarded by per-subject + global daily budget caps and per-identity rate limiting.
    return store.create_attempt(identity, title, question_id=question_id)


@router.get("/attempts", response_model=list[AttemptSummary])
async def list_attempts(identity: Identity = Depends(get_optional_identity)):
    _require_identity(identity)
    return store.list_attempts(identity)


@router.get("/attempts/{attempt_id}", response_model=SessionResult)
async def get_attempt(attempt_id: str, identity: Identity = Depends(get_optional_identity)):
    _require_identity(identity)
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return session


@router.post("/attempts/claim")
async def claim_attempts(request: Request, user_id: str = Depends(get_current_user)):
    """Transfer this request's guest attempts to the signed-in user.

    The guest token comes from the X-Guest-Token header (already attached by the
    API client), never from a caller-chosen body field.
    """
    guest = (request.headers.get("x-guest-token") or "").strip()
    transferred = guests.claim(user_id, guest) if guest else 0
    return {"transferred": transferred}


@router.post("/attempts/{attempt_id}/upload", response_model=SessionResult)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def upload_audio(
    request: Request,
    attempt_id: str,
    file: UploadFile = File(...),
    live_transcript: str = Form(""),
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")

    budget = get_budget_status()
    if budget.budget_exceeded:
        raise HTTPException(
            status_code=402,
            detail=f"Shared demo API budget cap of ${budget.cap_usd:.2f} reached.",
            headers={"X-CodeEcho-Error": "budget_exceeded"},
        )

    ext = Path(file.filename or "audio.webm").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio is too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB). "
            "Record a shorter response.",
        )
    _, storage_key = storage.save_audio(attempt_id, content, ext)
    session.audio_path = storage_key
    session.audio_url = storage.audio_url(storage_key)

    cleaned_live = live_transcript.strip()
    if cleaned_live:
        session.live_transcript = cleaned_live
    session_store.update_session(session)
    return session


def _find_audio(attempt_id: str) -> Path:
    audio_files = list(Path(settings.upload_dir).glob(f"{attempt_id}.*"))
    if audio_files:
        return audio_files[0]
    # Local copy is gone (e.g. ephemeral disk after a restart), re-fetch the
    # durable copy from Supabase Storage if it's configured.
    refetched = storage.ensure_local_audio(attempt_id)
    if refetched:
        return refetched
    raise HTTPException(status_code=400, detail="No audio uploaded for this attempt")


@router.post("/attempts/{attempt_id}/analyze", response_model=SessionResult)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def analyze_attempt(
    request: Request,
    attempt_id: str,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    session_store.update_session(session)
    audio_path = _find_audio(attempt_id)
    # Pipeline persists on COMPLETE/FAILED so a client disconnect cannot drop the row.
    return await run_analysis_pipeline(session, audio_path)


def _attempt_question(attempt_id: str, identity: Identity):
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if not session.question_id:
        raise HTTPException(
            status_code=400,
            detail="This attempt has no interview question attached.",
        )
    question = store.get_question(session.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question for this attempt not found")
    return session, question


@router.post("/attempts/{attempt_id}/score", response_model=Scorecard)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def score_attempt_route(
    request: Request,
    attempt_id: str,
    body: ScoreRequest = ScoreRequest(),
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session, question = _attempt_question(attempt_id, identity)
    try:
        scorecard = score_attempt(session, question, pseudocode=body.pseudocode)
    except BudgetExceededError as exc:
        raise HTTPException(
            status_code=402,
            detail=str(exc),
            headers={"X-CodeEcho-Error": "budget_exceeded"},
        )
    except ScoringUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
            headers={"X-CodeEcho-Error": "scoring_unavailable"},
        )
    except Exception:
        logger.exception("Scoring request failed for attempt %s", attempt_id)
        raise HTTPException(
            status_code=503,
            detail="Scoring is temporarily unavailable. Your transcript and delivery analysis are still available.",
            headers={"X-CodeEcho-Error": "scoring_unavailable"},
        )
    return store.save_scorecard(scorecard)


@router.post("/attempts/{attempt_id}/model-answer", response_model=ModelAnswer)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def model_answer_route(
    request: Request, attempt_id: str, identity: Identity = Depends(get_optional_identity)
):
    _require_identity(identity)
    _, question = _attempt_question(attempt_id, identity)
    try:
        return model_answer(question)
    except BudgetExceededError as exc:
        raise HTTPException(
            status_code=402,
            detail=str(exc),
            headers={"X-CodeEcho-Error": "budget_exceeded"},
        )
    except ScoringUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
            headers={"X-CodeEcho-Error": "scoring_unavailable"},
        )


@router.get("/attempts/{attempt_id}/scorecard", response_model=Scorecard)
async def get_scorecard_route(
    attempt_id: str, identity: Identity = Depends(get_optional_identity)
):
    _require_identity(identity)
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    scorecard = store.get_scorecard(attempt_id)
    if not scorecard:
        raise HTTPException(status_code=404, detail="No scorecard for this attempt yet")
    return scorecard


# --- mock interviews --------------------------------------------------------

def _interview_response(session, turn, question) -> InterviewQuestionResponse:
    if turn is None or question is None:
        return InterviewQuestionResponse(done=True, session_id=session.session_id)
    return InterviewQuestionResponse(
        done=False,
        session_id=session.session_id,
        turn_id=turn.turn_id,
        question=question,
        is_followup=turn.is_followup,
        progress=interview._progress_label(session, turn),
    )


@router.post("/interviews", response_model=InterviewQuestionResponse)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def start_interview_route(
    request: Request,
    body: StartInterviewRequest,
    background_tasks: BackgroundTasks,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session, turn, question = interview.start_interview(
        mode=body.mode,
        section=body.section,
        role=body.role,
        seniority=body.seniority,
        num_behavioral=body.num_behavioral,
        identity=identity,
    )
    # Warm the next main question while the candidate answers the first one.
    background_tasks.add_task(interview.prefetch_main, session, 1, identity)
    return _interview_response(session, turn, question)


@router.post("/interviews/{interview_id}/advance", response_model=InterviewQuestionResponse)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def advance_interview_route(
    request: Request,
    interview_id: str,
    body: AdvanceInterviewRequest,
    background_tasks: BackgroundTasks,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_interview(interview_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Prefer the client-provided live transcript so this call can run in parallel with
    # server-side analysis; fall back to the persisted attempt transcript otherwise.
    client_transcript = (body.transcript or "").strip()
    if client_transcript:
        transcript = client_transcript
    else:
        attempt = store.get_attempt(body.attempt_id, identity)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        transcript = (attempt.transcript_text or " ".join(w.word for w in attempt.words)).strip()
        if not transcript:
            # The answer hasn't finished analyzing yet. Retry shortly.
            raise HTTPException(
                status_code=409, detail="Answer is still being processed. Retry shortly."
            )

    turn, question = interview.decide_next(
        session, body.turn_id, body.attempt_id, transcript, identity
    )
    # Warm the main question after the one we just landed on, for its eventual transition.
    if turn is not None:
        background_tasks.add_task(
            interview.prefetch_main, session, turn.plan_index + 1, identity
        )
    return _interview_response(session, turn, question)


@router.get("/interviews", response_model=list[InterviewSession])
async def list_interviews_route(identity: Identity = Depends(get_optional_identity)):
    _require_identity(identity)
    return store.list_interviews(identity)


@router.get("/interviews/{interview_id}", response_model=InterviewSession)
async def get_interview_route(
    interview_id: str, identity: Identity = Depends(get_optional_identity)
):
    _require_identity(identity)
    session = store.get_interview(interview_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    return session


@router.get("/interviews/{interview_id}/current", response_model=InterviewQuestionResponse)
async def current_interview_turn_route(
    interview_id: str, identity: Identity = Depends(get_optional_identity)
):
    """The turn a resumed interview should land on.

    Returns the same shape as start/advance, so resuming is the client's ordinary
    "here is your next question" path rather than a second code path that can drift
    from it. ``done`` is true once every turn has been answered, which is the signal
    to go build the report instead.

    Read-only and idempotent: it derives the pending turn from the append-only turns
    log and never appends one, so polling it cannot advance the interview.
    """
    _require_identity(identity)
    session = store.get_interview(interview_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    turn = interview.pending_turn(session)
    question = store.get_question(turn.question_id) if turn else None
    return _interview_response(session, turn, question)


@router.post("/interviews/{interview_id}/report", response_model=InterviewReport)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def interview_report_route(
    request: Request,
    interview_id: str,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_interview(interview_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview.build_report(session, identity)


@router.get("/attempts/{attempt_id}/stream")
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def stream_analysis(
    request: Request,
    attempt_id: str,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_attempt(attempt_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    session_store.update_session(session)
    audio_path = _find_audio(attempt_id)
    event_queue: asyncio.Queue = asyncio.Queue()

    def on_event(event: str, data: dict) -> None:
        event_queue.put_nowait((event, data))

    async def event_generator():
        task = asyncio.create_task(run_analysis_pipeline(session, audio_path, on_event))
        try:
            while True:
                if task.done() and event_queue.empty():
                    break
                try:
                    event, data = await asyncio.wait_for(event_queue.get(), timeout=2)
                    yield {"event": event, "data": json.dumps(data)}
                    if event in ("complete", "error"):
                        break
                except asyncio.TimeoutError:
                    if task.done():
                        while not event_queue.empty():
                            event, data = event_queue.get_nowait()
                            yield {"event": event, "data": json.dumps(data)}
                            if event in ("complete", "error"):
                                break
                        break
                    yield {"event": "ping", "data": "{}"}
        finally:
            if not task.done():
                task.cancel()
            else:
                await task

    return EventSourceResponse(event_generator())


# --- static media (local fallback) ------------------------------------------

def _safe_media_path(directory: str, filename: str) -> Path:
    """Resolve ``filename`` strictly inside ``directory``.

    Guards against path traversal (e.g. '../.env', encoded separators) that could
    otherwise read arbitrary files such as the backend .env. Bare filenames only.
    """
    base = Path(directory).resolve()
    candidate = (base / filename).resolve()
    if base != candidate and base not in candidate.parents:
        raise HTTPException(status_code=404, detail="Not found")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return candidate


@router.get("/audio/{filename}")
async def serve_audio(
    filename: str,
    request: Request,
    identity: Identity = Depends(get_optional_identity),
):
    if not storage.verify_media_sig(
        filename, request.query_params.get("exp"), request.query_params.get("sig")
    ):
        _require_identity(identity)
        attempt_id = Path(filename).stem
        if not store.get_attempt(attempt_id, identity):
            raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(_safe_media_path(settings.upload_dir, filename))


@router.get("/clips/{filename}")
async def serve_clip(
    filename: str,
    request: Request,
    identity: Identity = Depends(get_optional_identity),
):
    if not storage.verify_media_sig(
        filename, request.query_params.get("exp"), request.query_params.get("sig")
    ):
        _require_identity(identity)
        stem = Path(filename).stem
        attempt_id = stem.rsplit("_", 1)[0] if "_" in stem else stem
        if not store.get_attempt(attempt_id, identity):
            raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(_safe_media_path(settings.clips_dir, filename))
