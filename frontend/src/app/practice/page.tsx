"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  createAttempt,
  getBudget,
  getHealth,
  getAttempt,
  getModelAnswer,
  getStreamUrl,
  scoreAttempt,
  uploadAudio,
} from "@/lib/api";
import type { BudgetStatus, ModelAnswer, Question, Scorecard, SessionMetrics, SessionResult, WordTimestamp, FillerOccurrence, PauseOccurrence } from "@/lib/types";
import { Nav } from "@/components/Nav";
import { Waveform } from "@/components/Waveform";
import { AudioRecorder, FileUpload } from "@/components/AudioInput";
import type { RecordingResult } from "@/components/AudioInput";
import { ProcessingSteps } from "@/components/TranscriptView";
import { TranscriptView } from "@/components/TranscriptView";
import { QuestionSetup } from "@/components/QuestionSetup";
import { ProblemPanel } from "@/components/ProblemPanel";
import { SpeakLexicon } from "@/components/SpeakLexicon";
import { ScorecardGrid } from "@/components/ScorecardGrid";
import { SketchButton } from "@/components/sketch/SketchButton";
import { Scratchpad } from "@/components/Scratchpad";
import { AnswerScaffold } from "@/components/AnswerScaffold";
import { ModelAnswerPanel } from "@/components/ModelAnswer";

type AppState = "setup" | "processing" | "results";

export default function Practice() {
  const [appState, setAppState] = useState<AppState>("setup");
  const [inputMode, setInputMode] = useState<"record" | "upload">("record");
  const [session, setSession] = useState<SessionResult | null>(null);
  const [processingStep, setProcessingStep] = useState<
    "uploading" | "transcribing" | "analyzing" | "complete" | "error"
  >("uploading");
  const [words, setWords] = useState<WordTimestamp[]>([]);
  const [transcriptText, setTranscriptText] = useState<string>("");
  const [transcriptStreaming, setTranscriptStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [transcriptSource, setTranscriptSource] = useState<string | null>(null);
  const [fillers, setFillers] = useState<FillerOccurrence[]>([]);
  const [pauses, setPauses] = useState<PauseOccurrence[]>([]);
  const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mockMode, setMockMode] = useState(false);
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState<Question | null>(null);
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [scoring, setScoring] = useState(false);
  const [scoreError, setScoreError] = useState<string | null>(null);
  const [attemptNum, setAttemptNum] = useState(1);
  const [prevScore, setPrevScore] = useState<number | null>(null);
  const [scratch, setScratch] = useState("");
  const [modelAns, setModelAns] = useState<ModelAnswer | null>(null);
  const [modelLoading, setModelLoading] = useState(false);
  // Results flow: analysis (Speak Lexicon) first, then the scorecard grid.
  const [resultsView, setResultsView] = useState<"lexicon" | "scores">("lexicon");

  const eventSourceRef = useRef<EventSource | null>(null);
  const completedRef = useRef(false);
  const questionRef = useRef<Question | null>(null);
  const scratchRef = useRef("");

  const updateScratch = (v: string) => {
    scratchRef.current = v;
    setScratch(v);
  };

  useEffect(() => {
    getHealth().then((h) => setMockMode(h.mock_mode)).catch(() => {});
    getBudget().then(setBudget).catch(() => {});
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  const closeStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const finishWithSession = useCallback(async (sessionId: string) => {
    closeStream();
    setProcessingStep("complete");
    const final = await getAttempt(sessionId);
    setSession(final);
    setWords(final.words);
    setFillers(final.fillers);
    setPauses(final.pauses ?? []);
    setMetrics(final.metrics);
    setResultsView("lexicon");
    setAppState("results");
    setLoading(false);
    getBudget().then(setBudget).catch(() => {});

    if (questionRef.current) {
      const isCoding =
        questionRef.current.qtype === "technical" &&
        questionRef.current.meta?.track !== "project";
      const pseudocode = isCoding ? scratchRef.current : undefined;
      setScoring(true);
      setScorecard(null);
      setScoreError(null);
      setModelAns(null);
      try {
        setScorecard(await scoreAttempt(sessionId, pseudocode));
      } catch (err) {
        setScorecard(null);
        setScoreError(err instanceof Error ? err.message : "Scoring failed");
      } finally {
        setScoring(false);
        getBudget().then(setBudget).catch(() => {});
      }
    }
  }, [closeStream]);

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
            await finishWithSession(sessionId);
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
              await finishWithSession(sessionId);
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
    [closeStream, finishWithSession]
  );

  const startAnalysis = useCallback(
    async (blob: Blob, filename: string, liveTranscript?: string) => {
      if (blob.size < 1000) {
        setError("That recording is too short. Aim for at least a few seconds.");
        return;
      }
      closeStream();
      completedRef.current = false;
      setLoading(true);
      setError(null);
      setAppState("processing");
      setProcessingStep("uploading");
      setWords([]);
      setTranscriptText("");
      setTranscriptStreaming(true);
      setStatusMessage(null);
      setTranscriptSource(null);
      setFillers([]);
      setPauses([]);
      setMetrics(null);
      setSession(null);
      try {
        const newSession = await createAttempt("Practice attempt", questionRef.current?.id);
        setSession(newSession);
        await uploadAudio(newSession.session_id, blob, filename, liveTranscript);
        setProcessingStep("transcribing");
        setStatusMessage("Transcribing…");
        await runStreamAnalysis(newSession.session_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong");
        setProcessingStep("error");
        setLoading(false);
        closeStream();
      }
    },
    [closeStream, runStreamAnalysis]
  );

  const handleRecording = ({ blob, liveTranscript }: RecordingResult) =>
    startAnalysis(blob, "recording.webm", liveTranscript);
  const handleFile = (file: File) => startAnalysis(file, file.name);

  const handleQuestionReady = (q: Question) => {
    questionRef.current = q;
    setQuestion(q);
    setAttemptNum(1);
    setPrevScore(null);
    updateScratch("");
  };

  const revealModelAnswer = async () => {
    if (!session) return;
    setModelLoading(true);
    try {
      setModelAns(await getModelAnswer(session.session_id));
    } catch {
      setModelAns(null);
    } finally {
      setModelLoading(false);
      getBudget().then(setBudget).catch(() => {});
    }
  };

  const resetAttemptState = () => {
    closeStream();
    completedRef.current = false;
    setSession(null);
    setScorecard(null);
    setScoring(false);
    setScoreError(null);
    setWords([]);
    setTranscriptText("");
    setTranscriptStreaming(false);
    setStatusMessage(null);
    setTranscriptSource(null);
    setFillers([]);
    setMetrics(null);
    setError(null);
    setLoading(false);
    setProcessingStep("uploading");
  };

  // Feedback loop: same question, fresh take (keep scratchpad to refine).
  const handleRetry = () => {
    setPrevScore(scorecard?.overall_score ?? prevScore);
    setAttemptNum((n) => n + 1);
    setModelAns(null);
    resetAttemptState();
    setAppState("setup");
  };

  // Brand new question.
  const handleNewQuestion = () => {
    questionRef.current = null;
    setQuestion(null);
    setAttemptNum(1);
    setPrevScore(null);
    setModelAns(null);
    updateScratch("");
    resetAttemptState();
    setAppState("setup");
  };

  const fillerIndices = new Set(fillers.map((f) => f.index));
  const delta =
    scorecard && prevScore !== null ? scorecard.overall_score - prevScore : null;

  // Technical has three tracks: coding (scratchpad/examples), project, system_design.
  const qTrack = question?.meta?.track as string | undefined;
  const isCodingQ =
    question?.qtype === "technical" && (qTrack === "coding" || qTrack == null);
  const TRACK_LABELS: Record<string, string> = {
    project: "project",
    system_design: "system design",
  };
  const typeLabel = !question
    ? ""
    : question.qtype === "technical"
    ? TRACK_LABELS[qTrack ?? ""] ?? "technical"
    : "behavioral";
  const scaffoldKind =
    question?.qtype === "technical" && qTrack && qTrack !== "coding"
      ? qTrack
      : question?.qtype ?? "behavioral";

  return (
    <main className="min-h-screen flex flex-col">
      <Nav />
      <div className="max-w-7xl mx-auto px-8 py-10 w-full flex-1 flex flex-col justify-center">
        {appState === "setup" && budget?.budget_exceeded && (
          <div className="panel p-5 text-center text-sm" style={{ color: "var(--amber)" }}>
            LLM budget cap reached — practice is paused.
          </div>
        )}

        {/* Setup screen — pick type + level (circles); then a separate answer screen. */}
        {appState === "setup" && !budget?.budget_exceeded && !question && (
          <QuestionSetup onReady={handleQuestionReady} disabled={loading} />
        )}

        {/* Answer screen — question + recorder, single centered column (no left rail). */}
        {appState === "setup" && !budget?.budget_exceeded && question && (
          <div className="max-w-4xl mx-auto w-full space-y-5">
            <div className="flex items-center justify-between">
              <span className="eyebrow">
                {typeLabel} · attempt {attemptNum}
                {prevScore !== null && ` · beat ${prevScore.toFixed(1)}/5`}
              </span>
              <button
                onClick={handleNewQuestion}
                disabled={loading}
                className="text-xs mono text-muted hover:text-echo"
              >
                new question
              </button>
            </div>

            <ProblemPanel question={question} />

            {isCodingQ && <Scratchpad value={scratch} onChange={updateScratch} disabled={loading} />}
            {attemptNum >= 2 && <AnswerScaffold qtype={scaffoldKind} />}

            <div className="pt-2">
              <div className="flex gap-2 mb-3">
                {(["record", "upload"] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setInputMode(mode)}
                    className={`px-4 py-2 text-sm font-medium capitalize transition-all ${
                      inputMode === mode ? "tab-active" : "tab-inactive"
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
              {inputMode === "record" ? (
                <AudioRecorder onRecordingComplete={handleRecording} disabled={loading} />
              ) : (
                <FileUpload onFileSelect={handleFile} disabled={loading} />
              )}
            </div>
          </div>
        )}

        {appState === "processing" && (
          <div className="space-y-6">
            <div className="flex flex-col items-center gap-4 py-4">
              <Waveform bars={32} active height={48} />
              <h2 className="font-display text-lg font-semibold">Analyzing your answer…</h2>
            </div>
            <ProcessingSteps step={processingStep} mockMode={mockMode} statusMessage={statusMessage} />
            {transcriptSource === "live" && (
              <div className="panel p-4 text-sm text-center" style={{ color: "var(--amber)" }}>
                Using the browser live transcript — Gemini audio transcription was unavailable.
              </div>
            )}
            {(words.length > 0 || transcriptText || processingStep === "transcribing") && (
              <TranscriptView
                words={words}
                fillerIndices={fillerIndices}
                fillers={fillers}
                pauses={pauses}
                streaming={transcriptStreaming}
                transcriptText={transcriptText}
                label={words.length === 0 && transcriptText ? "Live transcript (refining…)" : undefined}
              />
            )}
            {error && (
              <div className="panel p-5 text-center text-sm" style={{ color: "#f87171" }}>
                {error}
                <button onClick={handleRetry} className="block mx-auto mt-3 btn btn-ghost">
                  Try again
                </button>
              </div>
            )}
          </div>
        )}

        {appState === "results" && session && resultsView === "lexicon" && (
          <SpeakLexicon session={session} onNext={() => setResultsView("scores")} />
        )}

        {appState === "results" && session && resultsView === "scores" && (
          <div className="space-y-6">
            {scoring && (
              <div className="panel p-8 flex flex-col items-center gap-3">
                <Waveform bars={24} active height={36} />
                <p className="text-sm text-muted">Scoring your answer against the rubric…</p>
              </div>
            )}

            {scorecard && (
              <ScorecardGrid
                scorecard={scorecard}
                footer={
                  <div className="space-y-4">
                    {delta !== null && (
                      <p className="text-center text-sm mono">
                        {delta >= 0 ? (
                          <span className="text-echo">▲ +{delta.toFixed(1)} vs last attempt</span>
                        ) : (
                          <span style={{ color: "var(--amber)" }}>▼ {delta.toFixed(1)} vs last attempt</span>
                        )}
                      </p>
                    )}
                    {modelAns ? (
                      <ModelAnswerPanel answer={modelAns} />
                    ) : (
                      <button
                        onClick={revealModelAnswer}
                        disabled={modelLoading}
                        className="btn btn-ghost w-full"
                      >
                        {modelLoading ? "Writing model answer…" : "Reveal model answer"}
                      </button>
                    )}
                    <div className="flex flex-wrap gap-3 justify-center">
                      <button onClick={() => setResultsView("lexicon")} className="btn btn-ghost">
                        ← Back to lexicon
                      </button>
                      <SketchButton onClick={handleRetry}>Retry this question</SketchButton>
                      <SketchButton variant="ghost" onClick={handleNewQuestion}>
                        New question
                      </SketchButton>
                    </div>
                  </div>
                }
              />
            )}

            {!scoring && !scorecard && (
              <div className="panel p-6 text-center space-y-4">
                <p className="text-sm text-muted">
                  Couldn&rsquo;t score this answer — but your Speak Lexicon is still available.
                </p>
                {scoreError && (
                  <p className="text-xs mono text-muted/80 max-w-md mx-auto">{scoreError}</p>
                )}
                <div className="flex gap-3 justify-center">
                  <SketchButton onClick={handleRetry}>Retry</SketchButton>
                  <SketchButton variant="ghost" onClick={handleNewQuestion}>New question</SketchButton>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
