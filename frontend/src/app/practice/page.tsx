"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getBudget, getHealth, getModelAnswer, scoreAttempt } from "@/lib/api";
import type { BudgetStatus, ModelAnswer, Question, Scorecard } from "@/lib/types";
import { recordingCapSec } from "@/lib/types";
import { useAttemptAnalysis } from "@/lib/useAttemptAnalysis";
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
import { ScoringLoader } from "@/components/ScoringLoader";

type AppState = "setup" | "processing" | "results";

export default function Practice() {
  // record -> upload -> SSE -> delivery metrics, shared with /interview.
  // Scoring stays here: practice shows a score immediately, the interview hides
  // every score until the final report. That split is why the hook does not score.
  const analysis = useAttemptAnalysis();
  const {
    session,
    processingStep,
    words,
    transcriptText,
    transcriptStreaming,
    statusMessage,
    transcriptSource,
    fillers,
    pauses,
    error,
  } = analysis;

  const [appState, setAppState] = useState<AppState>("setup");
  const [inputMode, setInputMode] = useState<"record" | "upload">("record");
  const [mockMode, setMockMode] = useState(false);
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState<Question | null>(null);
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [scoring, setScoring] = useState(false);
  const [showScorecard, setShowScorecard] = useState(false);
  const [scoreError, setScoreError] = useState<string | null>(null);
  const [attemptNum, setAttemptNum] = useState(1);
  const [prevScore, setPrevScore] = useState<number | null>(null);
  const [scratch, setScratch] = useState("");
  const [modelAns, setModelAns] = useState<ModelAnswer | null>(null);
  const [modelLoading, setModelLoading] = useState(false);
  // Results flow: analysis (Speak Lexicon) first, then the scorecard grid.
  const [resultsView, setResultsView] = useState<"lexicon" | "scores">("lexicon");
  // State, not a ref: ScoringLoader renders from this, and a ref mutation would
  // not schedule the re-render that shows the updated elapsed time.
  const [scoringStartedAt, setScoringStartedAt] = useState<number | null>(null);

  const questionRef = useRef<Question | null>(null);
  const scratchRef = useRef("");

  const refreshBudget = useCallback(() => {
    getBudget().then(setBudget).catch(() => {});
  }, []);

  const updateScratch = (v: string) => {
    scratchRef.current = v;
    setScratch(v);
  };

  useEffect(() => {
    getHealth().then((h) => setMockMode(h.mock_mode)).catch(() => {});
    refreshBudget();
  }, [refreshBudget]);

  const scoreCurrentAttempt = useCallback(
    async (attemptId: string) => {
      if (!questionRef.current) return;
      // The scratchpad is only part of the answer for coding problems.
      const isCoding =
        questionRef.current.qtype === "technical" &&
        questionRef.current.meta?.track !== "project";
      const pseudocode = isCoding ? scratchRef.current : undefined;

      setScoring(true);
      setShowScorecard(false);
      setScoringStartedAt(Date.now());
      setScorecard(null);
      setScoreError(null);
      setModelAns(null);
      try {
        setScorecard(await scoreAttempt(attemptId, pseudocode));
      } catch (err) {
        setScorecard(null);
        setScoreError(err instanceof Error ? err.message : "Scoring failed");
        setScoring(false);
        setScoringStartedAt(null);
      } finally {
        refreshBudget();
      }
    },
    [refreshBudget]
  );

  const startAnalysis = useCallback(
    async (blob: Blob, filename: string, liveTranscript?: string) => {
      setLoading(true);
      setAppState("processing");
      let attemptId: string;
      try {
        attemptId = await analysis.start(blob, filename, {
          liveTranscript,
          questionId: questionRef.current?.id,
          title: "Practice attempt",
        });
      } catch {
        // The hook has already put the reason in `error`, which the processing
        // view renders along with a retry. Nothing to add here.
        setLoading(false);
        return;
      }
      setResultsView("lexicon");
      setAppState("results");
      setLoading(false);
      refreshBudget();
      await scoreCurrentAttempt(attemptId);
    },
    [analysis, refreshBudget, scoreCurrentAttempt]
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
      refreshBudget();
    }
  };

  const resetAttemptState = () => {
    analysis.reset();
    setScorecard(null);
    setScoring(false);
    setShowScorecard(false);
    setScoringStartedAt(null);
    setScoreError(null);
    setLoading(false);
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
    <main className="min-h-dvh flex flex-col overflow-x-hidden">
      <Nav />
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 w-full flex-1 flex flex-col justify-center">
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
            <div className="flex flex-wrap items-center justify-between gap-2">
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
                <AudioRecorder
                  onRecordingComplete={handleRecording}
                  disabled={loading}
                  maxDurationSec={recordingCapSec(question, session?.max_duration_sec)}
                />
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
                Using the browser live transcript — audio transcription was unavailable.
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
            {scoring && !showScorecard && (
              <ScoringLoader
                active={scoring}
                complete={!!scorecard}
                startedAt={scoringStartedAt}
                onReady={() => {
                  setShowScorecard(true);
                  setScoring(false);
                  setScoringStartedAt(null);
                }}
              />
            )}

            {showScorecard && scorecard && (
              <ScorecardGrid
                scorecard={scorecard}
                transcript={{
                  words: session.words,
                  transcriptText: session.transcript_text,
                  pauses: session.pauses,
                  fillers: session.fillers,
                }}
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
