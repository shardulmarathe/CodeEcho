"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  createAttempt,
  getAttempt,
  getStreamUrl,
  uploadAudio,
} from "@/lib/api";
import type {
  FillerOccurrence,
  PauseOccurrence,
  SessionMetrics,
  SessionResult,
  WordTimestamp,
} from "@/lib/types";

export type ProcessingStep =
  | "uploading"
  | "transcribing"
  | "analyzing"
  | "complete"
  | "error";

export interface StartOptions {
  liveTranscript?: string;
  questionId?: string;
  title?: string;
}

/**
 * Owns the full record→upload→SSE-stream→delivery-metrics lifecycle for a single
 * recorded answer. Shared by /practice and /interview. It deliberately does NOT
 * score — `start()` resolves with the finished attempt id and the caller decides
 * what happens next (practice scores; interview advances to the next question).
 */
export function useAttemptAnalysis() {
  const [session, setSession] = useState<SessionResult | null>(null);
  const [processingStep, setProcessingStep] = useState<ProcessingStep>("uploading");
  const [words, setWords] = useState<WordTimestamp[]>([]);
  const [transcriptText, setTranscriptText] = useState<string>("");
  const [transcriptStreaming, setTranscriptStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [transcriptSource, setTranscriptSource] = useState<string | null>(null);
  const [fillers, setFillers] = useState<FillerOccurrence[]>([]);
  const [pauses, setPauses] = useState<PauseOccurrence[]>([]);
  const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const completedRef = useRef(false);

  const closeStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  useEffect(() => () => closeStream(), [closeStream]);

  const reset = useCallback(() => {
    closeStream();
    completedRef.current = false;
    setSession(null);
    setWords([]);
    setTranscriptText("");
    setTranscriptStreaming(false);
    setStatusMessage(null);
    setTranscriptSource(null);
    setFillers([]);
    setPauses([]);
    setMetrics(null);
    setError(null);
    setProcessingStep("uploading");
  }, [closeStream]);

  // Pull the finished session and populate final state. Resolves; does NOT score.
  const finish = useCallback(
    async (sessionId: string): Promise<SessionResult> => {
      closeStream();
      setProcessingStep("complete");
      const final = await getAttempt(sessionId);
      setSession(final);
      setWords(final.words);
      setFillers(final.fillers);
      setPauses(final.pauses ?? []);
      setMetrics(final.metrics);
      return final;
    },
    [closeStream]
  );

  const runStreamAnalysis = useCallback(
    (sessionId: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        completedRef.current = false;
        closeStream();
        const es = new EventSource(getStreamUrl(sessionId));
        eventSourceRef.current = es;

        const handleServerError = (message: string) => {
          if (completedRef.current) return;
          completedRef.current = true;
          closeStream();
          reject(new Error(message));
        };

        es.addEventListener("status", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          if (data.status) setProcessingStep(data.status);
          if (data.message) setStatusMessage(data.message);
        });
        es.addEventListener("transcript_source", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setTranscriptSource(data.source || null);
          if (data.message) setStatusMessage(data.message);
        });
        es.addEventListener("transcript_partial", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setWords(data.words);
          setTranscriptText(data.transcript_text || "");
          setTranscriptStreaming(!data.complete);
          setProcessingStep("transcribing");
        });
        es.addEventListener("transcript", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setWords(data.words);
          setTranscriptText(data.transcript_text || "");
          setTranscriptStreaming(false);
          setProcessingStep("transcribing");
        });
        es.addEventListener("fillers", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setFillers(data.fillers);
          setProcessingStep("analyzing");
          setStatusMessage("Computing delivery metrics…");
        });
        es.addEventListener("pauses", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setPauses(data.pauses);
        });
        es.addEventListener("metrics", (e) => {
          const data = JSON.parse((e as MessageEvent).data);
          setMetrics(data.metrics);
        });
        es.addEventListener("complete", async () => {
          completedRef.current = true;
          try {
            await finish(sessionId);
            resolve();
          } catch (err) {
            reject(err);
          }
        });
        es.addEventListener("error", (e) => {
          if (completedRef.current) return;
          try {
            const data = JSON.parse((e as MessageEvent).data);
            handleServerError(data.error || "Analysis failed");
          } catch {
            // fall through to onerror
          }
        });
        es.onerror = async () => {
          if (completedRef.current) return;
          closeStream();
          try {
            const result = await getAttempt(sessionId);
            if (result.status === "complete") {
              completedRef.current = true;
              await finish(sessionId);
              resolve();
            } else if (result.status === "failed") {
              reject(new Error(result.error || "Analysis failed"));
            } else {
              reject(new Error("Analysis was interrupted. Please try again."));
            }
          } catch (err) {
            reject(err instanceof Error ? err : new Error("Analysis failed"));
          }
        };
      });
    },
    [closeStream, finish]
  );

  /**
   * Begin record→analyze for one answer but hand the attempt id back EARLY — as soon
   * as the attempt exists — and return a `completion` promise that resolves once
   * upload + transcription + delivery metrics finish. Lets the caller kick off other
   * work (e.g. advancing the interview) in parallel with the analysis instead of after.
   *
   * The caller MUST await a prior `completion` before calling this again: analysis uses
   * a single stream, and `reset()` here would otherwise tear down an in-flight one.
   */
  const startDetached = useCallback(
    async (
      blob: Blob,
      filename: string,
      opts: StartOptions = {}
    ): Promise<{ attemptId: string; completion: Promise<void> }> => {
      if (blob.size < 1000) {
        const msg = "That recording is too short. Aim for at least a few seconds.";
        setError(msg);
        throw new Error(msg);
      }
      reset();
      setTranscriptStreaming(true);
      setProcessingStep("uploading");
      let newSession;
      try {
        newSession = await createAttempt(opts.title ?? "Attempt", opts.questionId);
        setSession(newSession);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong");
        setProcessingStep("error");
        closeStream();
        throw err;
      }
      const attemptId = newSession.session_id;
      const completion = (async () => {
        try {
          await uploadAudio(attemptId, blob, filename, opts.liveTranscript);
          setProcessingStep("transcribing");
          setStatusMessage("Transcribing…");
          await runStreamAnalysis(attemptId);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Something went wrong");
          setProcessingStep("error");
          closeStream();
          throw err;
        }
      })();
      return { attemptId, completion };
    },
    [reset, runStreamAnalysis, closeStream]
  );

  /**
   * Record→analyze a single answer. Resolves with the attempt id once analysis
   * completes (state is populated). Throws on failure (state set to "error").
   */
  const start = useCallback(
    async (blob: Blob, filename: string, opts: StartOptions = {}): Promise<string> => {
      const { attemptId, completion } = await startDetached(blob, filename, opts);
      await completion;
      return attemptId;
    },
    [startDetached]
  );

  return {
    // state
    session,
    processingStep,
    words,
    transcriptText,
    transcriptStreaming,
    statusMessage,
    transcriptSource,
    fillers,
    pauses,
    metrics,
    error,
    // setters a caller may need
    setError,
    setProcessingStep,
    // actions
    start,
    startDetached,
    reset,
    closeStream,
    finish,
  };
}
