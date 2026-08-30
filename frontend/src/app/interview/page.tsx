"use client";

import { useCallback, useRef, useState } from "react";
import { Nav } from "@/components/Nav";
import { InterviewSetup } from "@/components/InterviewSetup";
import { InterviewHistory } from "@/components/InterviewHistory";
import { InterviewSession } from "@/components/InterviewSession";
import { InterviewReport } from "@/components/InterviewReport";
import { useAttemptAnalysis } from "@/lib/useAttemptAnalysis";
import { useServiceReadiness } from "@/lib/useServiceReadiness";
import {
  ServiceStatusBanners,
  TranscriptionStatusBanner,
} from "@/components/ReliabilityBanners";
import {
  advanceInterview,
  getCurrentInterviewTurn,
  getInterviewReport,
} from "@/lib/api";
import type {
  InterviewQuestionResponse,
  InterviewReport as Report,
  InterviewSession as Session,
  Question,
} from "@/lib/types";
import type { RecordingResult } from "@/components/AudioInput";

type Phase = "setup" | "session" | "report";

// Advance, tolerating the brief 409 window where the just-finished answer is still
// being persisted on a different worker.
async function advanceWithRetry(
  interviewId: string,
  attemptId: string,
  turnId: string | null,
  transcript?: string
): Promise<InterviewQuestionResponse> {
  for (let i = 0; i < 4; i++) {
    try {
      return await advanceInterview(interviewId, attemptId, turnId ?? undefined, transcript);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      if (msg.toLowerCase().includes("still being processed") && i < 3) {
        await new Promise((r) => setTimeout(r, 1200));
        continue;
      }
      throw e;
    }
  }
  throw new Error("Could not advance the interview.");
}

export default function Interview() {
  const analysis = useAttemptAnalysis();
  const service = useServiceReadiness();
  const [phase, setPhase] = useState<Phase>("setup");
  const [question, setQuestion] = useState<Question | null>(null);
  const [turnId, setTurnId] = useState<string | null>(null);
  const [progress, setProgress] = useState("");
  const [isFollowup, setIsFollowup] = useState(false);
  const [busy, setBusy] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  const interviewIdRef = useRef<string | null>(null);
  // The previous answer's analysis, still finishing in the background while the
  // candidate moves to the next question. Awaited before the next answer (which
  // resets the shared analysis stream) and before building the final report.
  const pendingAnalysisRef = useRef<Promise<void> | null>(null);

  const applyNext = useCallback((r: InterviewQuestionResponse) => {
    setTurnId(r.turn_id ?? null);
    setQuestion(r.question ?? null);
    setProgress(r.progress);
    setIsFollowup(r.is_followup);
  }, []);

  const onStarted = useCallback(
    (r: InterviewQuestionResponse) => {
      interviewIdRef.current = r.session_id;
      setReport(null);
      setError(null);
      applyNext(r);
      setPhase("session");
    },
    [applyNext]
  );

  const finishInterview = useCallback(async (id: string) => {
    setBusy(true);
    try {
      setReport(await getInterviewReport(id));
      setPhase("report");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not build the report.");
    } finally {
      setBusy(false);
    }
  }, []);

  /** Rejoin an interview that was left unfinished.
   *
   * The turn to land on is derived server-side from the append-only log, so this
   * cannot disagree with where the interview actually is. If every turn turned out
   * to be answered, the thing that's missing is the report, not a question. */
  const onResume = useCallback(
    async (session: Session) => {
      const id = session.session_id;
      setBusy(true);
      setError(null);
      setReport(null);
      analysis.reset();
      pendingAnalysisRef.current = null;
      interviewIdRef.current = id;
      try {
        const next = await getCurrentInterviewTurn(id);
        if (next.done) {
          await finishInterview(id);
          return;
        }
        applyNext(next);
        setPhase("session");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not resume that interview.");
        interviewIdRef.current = null;
      } finally {
        setBusy(false);
      }
    },
    [analysis, applyNext, finishInterview]
  );

  const onViewReport = useCallback(
    async (session: Session) => {
      interviewIdRef.current = session.session_id;
      setError(null);
      // Clear first, or the previously viewed report flashes while this one loads.
      setReport(null);
      setPhase("report");
      await finishInterview(session.session_id);
    },
    [finishInterview]
  );

  const onAnswer = useCallback(
    async ({ blob, liveTranscript }: RecordingResult) => {
      const id = interviewIdRef.current;
      if (!id || !question) return;
      setError(null);
      setBusy(true);
      try {
        // Make sure the PREVIOUS answer's analysis has flushed before we reset the
        // shared analysis stream for this one. (A prior background failure is
        // non-blocking, that answer just misses delivery metrics in the report.)
        if (pendingAnalysisRef.current) {
          await pendingAnalysisRef.current.catch(() => {});
          pendingAnalysisRef.current = null;
        }

        // Record → transcribe → delivery metrics (no score; interview turns don't
        // count against the single-answer attempt quota). Hand back the attempt id
        // early so we can advance without waiting for transcription to finish.
        const { attemptId, completion } = await analysis.startDetached(blob, "answer.webm", {
          liveTranscript,
          questionId: question.id,
          title: "Interview answer",
        });

        const live = (liveTranscript ?? "").trim();
        let next: InterviewQuestionResponse;
        if (live) {
          // Fast path: advance in PARALLEL with transcription, using the live
          // transcript for the follow-up decision. Analysis finishes in the background.
          pendingAnalysisRef.current = completion.catch(() => {});
          next = await advanceWithRetry(id, attemptId, turnId, live);
        } else {
          // No live transcript (browser STT unavailable), wait for the server
          // transcript so follow-ups stay grounded in the real answer.
          await completion;
          next = await advanceWithRetry(id, attemptId, turnId);
        }

        if (next.done) {
          // The final answer must be fully analyzed before we build the report.
          if (pendingAnalysisRef.current) {
            await pendingAnalysisRef.current.catch(() => {});
            pendingAnalysisRef.current = null;
          }
          await finishInterview(id);
        } else {
          applyNext(next);
          setBusy(false);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
        setBusy(false);
      }
    },
    [analysis, question, turnId, applyNext, finishInterview]
  );

  const restart = useCallback(() => {
    analysis.reset();
    pendingAnalysisRef.current = null;
    interviewIdRef.current = null;
    setQuestion(null);
    setTurnId(null);
    setProgress("");
    setIsFollowup(false);
    setReport(null);
    setError(null);
    setBusy(false);
    setPhase("setup");
  }, [analysis]);

  return (
    <main className="min-h-dvh flex flex-col overflow-x-hidden">
      <Nav />
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 w-full flex-1 flex flex-col">
        <ServiceStatusBanners
          wakeState={service.wakeState}
          health={service.health}
          budget={service.budget}
          onRetry={service.retry}
        />
        <TranscriptionStatusBanner
          source={analysis.transcriptSource}
          errorCode={analysis.errorCode}
        />
        {phase !== "report" && (
          <div className="mb-8 text-center">
            <h1 className="hand text-4xl md:text-5xl font-bold">Mock Interview</h1>
            {phase === "setup" && (
              <p className="text-muted text-sm mt-2">
                A guided session with live follow-ups. One combined report at the end.
              </p>
            )}
          </div>
        )}

        {phase === "setup" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-12 pb-12 w-full">
            <InterviewSetup onStarted={onStarted} />
            <InterviewHistory
              onResume={onResume}
              onViewReport={onViewReport}
              disabled={busy}
            />
          </div>
        )}

        {phase === "session" && question && (
          <InterviewSession
            question={question}
            progress={progress}
            isFollowup={isFollowup}
            busy={busy}
            statusMessage={analysis.statusMessage}
            error={error}
            onAnswer={onAnswer}
          />
        )}

        {phase === "report" && report && (
          <InterviewReport report={report} onRestart={restart} />
        )}

        {phase === "report" && busy && !report && (
          <p className="text-sm text-muted text-center">Building your report…</p>
        )}
      </div>
    </main>
  );
}
