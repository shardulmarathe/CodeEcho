import asyncio
import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
    Question,
    Scorecard,
    ScoreRequest,
    SessionResult,
    StartInterviewRequest,
)
from app.services import guests, interview, questions, session_store, storage, store, usage
from app.services.auth import (
    Identity,
    clerk_configured,
    get_current_user,
    get_optional_identity,
)
from app.services.budget import get_budget_status
from app.services.llm_client import get_provider_label, is_configured
from app.services.pipeline import run_analysis_pipeline
from app.services.ratelimit import expensive_key, limiter
from app.services.scoring import ScoringUnavailable, model_answer, score_attempt
from app.services.supabase_client import is_configured as supabase_configured

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".webm", ".ogg", ".mp4"}
# A capped (1:30) answer is ~1 MB of opus/webm; 25 MB is generous headroom for other
# codecs while blocking disk-fill abuse. Over-long *duration* is rejected later in the
# pipeline (before any paid transcription); this only bounds raw upload size.
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


# --- meta -------------------------------------------------------------------

@router.get("/health")
async def health():
    configured = is_configured()
    return {
        "status": "ok",
        "gemini_configured": configured,
        "mock_mode": not configured,
        "transcription_provider": get_provider_label() if configured else "mock",
        "llm_model": settings.gemini_model,
        "transcription_model": settings.effective_transcription_model,
        "ffmpeg_available": bool(shutil.which("ffmpeg")),
        "google_gemini_base_url": settings.google_gemini_base_url or None,
        "clerk_configured": clerk_configured(),
        "supabase_configured": supabase_configured(),
    }


@router.get("/me")
async def me(identity: Identity = Depends(get_optional_identity)):
    return {
        "authenticated": identity.is_user,
        "user_id": identity.user_id,
        "clerk_configured": clerk_configured(),
    }


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
    q = questions.generate_question(
        qtype=body.qtype,
        role=body.role,
        seniority=body.seniority,
        difficulty=body.difficulty,
        topic=body.topic,
        track=body.track,
    )
    return store.create_question(q, owner_user_id=identity.user_id)


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
    return store.create_question(q, owner_user_id=identity.user_id)


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: str):
    q = store.get_question(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


# --- attempts ---------------------------------------------------------------

def _require_identity(identity: Identity) -> None:
    if not identity.is_user and not identity.is_guest:
        raise HTTPException(
            status_code=400,
            detail="Missing identity. Sign in or send an X-Guest-Token header.",
        )


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


class ClaimBody(BaseModel):
    guest_token: str


@router.post("/attempts/claim")
async def claim_attempts(
    request: Request, body: ClaimBody, user_id: str = Depends(get_current_user)
):
    """Transfer a guest's prior attempts to the now-authenticated user."""
    transferred = guests.claim(user_id, body.guest_token)
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
            status_code=402, detail=f"API budget cap of ${budget.cap_usd:.2f} reached."
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
            "Answers are capped at 1:30 — record a shorter response.",
        )
    _, storage_key = storage.save_audio(attempt_id, content, ext)
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
    # Local copy is gone (e.g. ephemeral disk after a restart) — re-fetch the
    # durable copy from Supabase Storage if it's configured.
    refetched = storage.ensure_local_audio(attempt_id)
    if refetched:
        return refetched
    raise HTTPException(status_code=400, detail="No audio uploaded for this attempt")


@router.post("/attempts/{attempt_id}/analyze", response_model=SessionResult)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def analyze_attempt(request: Request, attempt_id: str):
    usage.set_subject(usage.ip_subject(request))  # capability-style: bill against IP
    session = session_store.get_session(attempt_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
    audio_path = _find_audio(attempt_id)
    session = await run_analysis_pipeline(session, audio_path)
    store.persist_attempt_results(session)
    return session


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
    except ScoringUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
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
    except ScoringUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))


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
    return _interview_response(session, turn, question)


@router.post("/interviews/{interview_id}/advance", response_model=InterviewQuestionResponse)
@limiter.limit(settings.rate_limit_expensive, key_func=expensive_key)
async def advance_interview_route(
    request: Request,
    interview_id: str,
    body: AdvanceInterviewRequest,
    identity: Identity = Depends(get_optional_identity),
):
    _require_identity(identity)
    session = store.get_interview(interview_id, identity)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    attempt = store.get_attempt(body.attempt_id, identity)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    transcript = (attempt.transcript_text or " ".join(w.word for w in attempt.words)).strip()
    if not transcript:
        # Persist race (multi-worker): the answer hasn't finished analyzing. Retry shortly.
        raise HTTPException(status_code=409, detail="Answer is still being processed. Retry shortly.")
    turn, question = interview.decide_next(
        session, body.turn_id, body.attempt_id, transcript, identity
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
async def stream_analysis(request: Request, attempt_id: str):
    # Capability-style: the unguessable attempt id authorizes the stream (quota +
    # ownership were enforced at create/upload). EventSource cannot send headers.
    usage.set_subject(usage.ip_subject(request))  # bill against IP
    session = session_store.get_session(attempt_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attempt not found")
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
                store.persist_attempt_results(session)

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
async def serve_audio(filename: str):
    return FileResponse(_safe_media_path(settings.upload_dir, filename))


@router.get("/clips/{filename}")
async def serve_clip(filename: str):
    return FileResponse(_safe_media_path(settings.clips_dir, filename))
