"use client";

import { useCallback, useRef, useState } from "react";
import { Nav } from "@/components/Nav";
import { InterviewSetup } from "@/components/InterviewSetup";
import { InterviewSession } from "@/components/InterviewSession";
import { InterviewReport } from "@/components/InterviewReport";
import { useAttemptAnalysis } from "@/lib/useAttemptAnalysis";
import { advanceInterview, getInterviewReport } from "@/lib/api";
import type {
  InterviewQuestionResponse,
  InterviewReport as Report,
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
  const [phase, setPhase] = useState<Phase>("setup");
  const [interviewId, setInterviewId] = useState<string | null>(null);
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
      setInterviewId(r.session_id);
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

  const onAnswer = useCallback(
    async ({ blob, liveTranscript }: RecordingResult) => {
      const id = interviewIdRef.current;
      if (!id || !question) return;
      setError(null);
      setBusy(true);
      try {
        // Make sure the PREVIOUS answer's analysis has flushed before we reset the
        // shared analysis stream for this one. (A prior background failure is
        // non-blocking — that answer just misses delivery metrics in the report.)
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
          // No live transcript (browser STT unavailable) — wait for the server
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
    setInterviewId(null);
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
          <div className="flex-1 flex flex-col justify-center pb-12 w-full">
            <InterviewSetup onStarted={onStarted} />
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
