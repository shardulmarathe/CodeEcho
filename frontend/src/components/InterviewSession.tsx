"use client";

import type { Question } from "@/lib/types";
import { AudioRecorder } from "@/components/AudioInput";
import type { RecordingResult } from "@/components/AudioInput";
import { ProblemPanel } from "@/components/ProblemPanel";
import { Waveform } from "@/components/Waveform";

interface InterviewSessionProps {
  question: Question;
  progress: string; // "Question 2 of 3" | "Follow-up"
  isFollowup: boolean;
  busy: boolean; // analyzing the answer / fetching the next question
  statusMessage?: string | null;
  error?: string | null;
  onAnswer: (result: RecordingResult) => void;
}

// Single, centered column, the question on top, the recorder below. No left rail.
export function InterviewSession({
  question,
  progress,
  isFollowup,
  busy,
  statusMessage,
  error,
  onAnswer,
}: InterviewSessionProps) {
  return (
    <div className="max-w-4xl mx-auto w-full space-y-5">
      <div className="flex items-center gap-3">
        <span
          className="inline-block px-3 py-1 text-xs font-medium"
          style={
            isFollowup
              ? { background: "var(--surface-2)", color: "var(--fg)", border: "1px solid var(--border)", borderRadius: "9px 13px 9px 13px" }
              : { background: "var(--echo)", color: "var(--on-echo)", borderRadius: "9px 13px 9px 13px" }
          }
        >
          {isFollowup ? "Follow-up" : progress}
        </span>
        {isFollowup && <span className="text-xs text-muted">{progress}</span>}
      </div>

      <ProblemPanel question={question} />

      {busy ? (
        <div className="panel p-10 flex flex-col items-center gap-4 text-center">
          <Waveform bars={28} active height={40} />
          <p className="text-sm text-muted">{statusMessage || "Analyzing your answer…"}</p>
          <p className="text-xs text-muted">The interviewer is listening — next question in a moment.</p>
        </div>
      ) : (
        <AudioRecorder onRecordingComplete={onAnswer} disabled={busy} />
      )}
      {error && (
        <p className="text-sm text-center" style={{ color: "#f87171" }}>
          {error}
        </p>
      )}
    </div>
  );
}
