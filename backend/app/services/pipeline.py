"""Main analysis pipeline orchestrating transcription and filler detection."""

import asyncio
import logging
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

from app.config import settings
from app.models import SessionResult, SessionStatus
from app.services.analytics import compute_metrics
from app.services.audio_utils import AudioValidationError

# Allow a few seconds of slack over the hard cap so a recording that stops a beat
# late (client timer vs. actual encoded length) isn't rejected for being ~180.3s.
ANSWER_CAP_GRACE_SEC = 5
from app.services.budget import BudgetExceededError
from app.services.filler_detect import (
    classify_sentence_positions,
    detect_fillers,
    discourse_candidates,
    heuristic_discourse_fillers,
    high_confidence_discourse_fillers,
    make_filler,
)
from app.services.pause_detect import detect_pauses
from app.services.transition import classify_discourse_fillers, tag_fillers
from app.services.audio_utils import effective_duration_sec
from app.services.llm_client import is_configured
from app.services.session_store import update_session, get_session
from app.services import store
from app.services.transcribe import transcribe_audio, transcribe_audio_mock


async def run_analysis_pipeline(
    session: SessionResult,
    audio_path: Path,
    on_event: Callable[[str, dict], None] | None = None,
) -> SessionResult:
    """Run transcription + filler detection with optional SSE event callbacks."""

    def emit(event: str, data: dict) -> None:
        if on_event:
            on_event(event, data)

    try:
        session.words = []
        session.fillers = []
        session.pauses = []
        session.transcript_text = ""
        session.error = None
        from app.models import SessionMetrics
        session.metrics = SessionMetrics()

        audio_duration = effective_duration_sec(audio_path)

        # Hard cap on answer length. The recorder auto-stops at the cap; this is the
        # server-side backstop for uploaded files or a bypassed client. Reject BEFORE
        # transcription so an over-long answer never incurs LLM/transcription cost.
        cap = int(session.max_duration_sec or 180)
        cap = min(cap, settings.max_audio_duration_sec)
        if audio_duration > cap + ANSWER_CAP_GRACE_SEC:
            mins, secs = divmod(cap, 60)
            raise AudioValidationError(
                f"Answers are capped at {mins}:{secs:02d}. Please re-record a shorter response."
            )

        session.status = SessionStatus.TRANSCRIBING
        update_session(session)
        emit("status", {"status": "transcribing", "message": "Sending audio for transcription..."})

        if settings.transcription_configured:
            partial_queue: asyncio.Queue[tuple[list, str, bool]] = asyncio.Queue()

            def on_partial(words, text, complete):
                partial_queue.put_nowait((words, text, complete))

            async def run_transcribe():
                fresh = get_session(session.session_id)
                live = (
                    (fresh.live_transcript if fresh else None)
                    or session.live_transcript
                )
                return await asyncio.to_thread(
                    transcribe_audio,
                    audio_path,
                    on_partial=on_partial,
                    fallback_transcript=live,
                )

            transcribe_task = asyncio.create_task(run_transcribe())
            last_status = asyncio.get_event_loop().time()

            while not transcribe_task.done():
                drained = False
                while True:
                    try:
                        words_partial, text_partial, complete = partial_queue.get_nowait()
                        emit(
                            "transcript_partial",
                            {
                                "words": [w.model_dump() for w in words_partial],
                                "transcript_text": text_partial,
                                "complete": complete,
                            },
                        )
                        drained = True
                    except asyncio.QueueEmpty:
                        break

                now = asyncio.get_event_loop().time()
                if not drained and now - last_status >= 2:
                    emit(
                        "status",
                        {
                            "status": "transcribing",
                            "message": "Transcribing your answer...",
                        },
                    )
                    last_status = now

                await asyncio.sleep(0.2)

            while not partial_queue.empty():
                words_partial, text_partial, complete = partial_queue.get_nowait()
                emit(
                    "transcript_partial",
                    {
                        "words": [w.model_dump() for w in words_partial],
                        "transcript_text": text_partial,
                        "complete": complete,
                    },
                )

            words, transcript, duration, transcript_source = await transcribe_task
        else:
            await asyncio.sleep(1.5)
            words, transcript, duration = await asyncio.to_thread(
                transcribe_audio_mock, audio_path
            )
            transcript_source = "mock"

        if transcript_source == "live":
            emit(
                "transcript_source",
                {
                    "source": "live",
                    "message": "Using browser live transcript — audio transcription failed.",
                },
            )
        elif transcript_source == "mock":
            emit(
                "transcript_source",
                {
                    "source": "mock",
                    "message": "Demo transcription is using a sample transcript, not your recording.",
                },
            )
        else:
            emit("transcript_source", {"source": transcript_source})

        session.words = words
        session.transcript_text = transcript
        audio_duration = max(audio_duration, duration)
        update_session(session)

        emit(
            "transcript",
            {
                "words": [w.model_dump() for w in words],
                "transcript_text": transcript,
            },
        )

        session.status = SessionStatus.ANALYZING
        update_session(session)
        emit("status", {"status": "analyzing", "message": "Detecting filler words..."})

        fillers = detect_fillers(words)

        # Disambiguate discourse markers (like/actually/basically/literally) in context -
        # they're fillers in some sentences and meaningful in others, so a regex can't decide.
        candidates = discourse_candidates(words)
        if candidates:
            emit(
                "status",
                {"status": "analyzing", "message": "Checking 'like' and discourse fillers..."},
            )
            if is_configured():
                confirmed = await asyncio.to_thread(
                    classify_discourse_fillers, words, candidates
                )
                # Safety floor: the LLM under-detects "like" fillers (and a failed/empty
                # segment would otherwise drop them entirely). Union in the unambiguous
                # heuristic hits ("I was like", "it's, like, fast") so they're never missed.
                confirmed |= high_confidence_discourse_fillers(words, candidates)
            else:
                confirmed = heuristic_discourse_fillers(words, candidates)
            for idx in confirmed:
                fillers.append(make_filler(words, idx))
            fillers.sort(key=lambda f: f.index)

        fillers = classify_sentence_positions(words, fillers)
        session.fillers = fillers
        update_session(session)

        emit(
            "fillers",
            {"fillers": [f.model_dump() for f in fillers]},
        )

        # Detect silent pauses and surface them in the transcript + metrics for
        # communication analysis. Real audio uses ffmpeg silence detection; the mock
        # transcript has no matching audio, so fall back to its timestamp gaps.
        pause_audio = None if transcript_source == "mock" else audio_path
        pauses = detect_pauses(words, audio_path=pause_audio)
        session.pauses = pauses
        update_session(session)
        emit("pauses", {"pauses": [p.model_dump() for p in pauses]})

        # Tag *why* each filler occurred (idea transition / topic / hesitation)
        if fillers:
            emit(
                "status",
                {"status": "analyzing", "message": "Tagging filler patterns..."},
            )
            tags = await asyncio.to_thread(tag_fillers, words, fillers)
            for filler in fillers:
                tag_info = tags.get(filler.index)
                if not tag_info:
                    continue
                filler.tag = tag_info.get("tag")
                filler.tag_reason = tag_info.get("reason")
                filler.topic = tag_info.get("topic")
                filler.is_transition_related = tag_info.get("tag") == "idea_transition"
            session.fillers = fillers
            update_session(session)
            emit("fillers", {"fillers": [f.model_dump() for f in fillers]})

        metrics = compute_metrics(
            words, fillers, duration_sec=audio_duration, pauses=pauses
        )
        session.metrics = metrics
        update_session(session)
        emit("metrics", {"metrics": metrics.model_dump()})

        emit(
            "analytics",
            {
                "position_breakdown": metrics.position_breakdown.model_dump(),
                "tag_breakdown": metrics.tag_breakdown,
                "transition_filler_pct": metrics.transition_filler_pct,
                "long_pause_filler_pct": metrics.long_pause_filler_pct,
                "avg_pause_before_filler_sec": metrics.avg_pause_before_filler_sec,
                "avg_pause_elsewhere_sec": metrics.avg_pause_elsewhere_sec,
            },
        )

        session.status = SessionStatus.COMPLETE
        update_session(session)
        emit("complete", {"session_id": session.session_id})
        store.persist_attempt_results(session)

    except BudgetExceededError as e:
        session.status = SessionStatus.FAILED
        session.error = str(e)
        update_session(session)
        emit("error", {"error": str(e), "code": "budget_exceeded"})
        store.persist_attempt_results(session)
    except AudioValidationError as e:
        # Safe, user-facing message (silent/too-short/too-quiet audio), surface it so
        # the user knows to re-record, rather than a generic failure.
        session.status = SessionStatus.FAILED
        session.error = str(e)
        update_session(session)
        emit("error", {"error": str(e), "code": "audio_invalid"})
        store.persist_attempt_results(session)
    except Exception:
        # Log the full detail server-side; never return raw exception text to the
        # client (it can carry internal paths, request URLs, or credentials).
        logger.exception("Analysis pipeline failed for session %s", session.session_id)
        failed_during_stt = session.status == SessionStatus.TRANSCRIBING
        generic = (
            "Audio transcription failed. Please retry or use a supported audio file."
            if failed_during_stt
            else "Analysis failed. Please try again."
        )
        session.status = SessionStatus.FAILED
        session.error = generic
        update_session(session)
        emit(
            "error",
            {"error": generic, "code": "stt_failed" if failed_during_stt else "analysis_failed"},
        )
        store.persist_attempt_results(session)

    return session
