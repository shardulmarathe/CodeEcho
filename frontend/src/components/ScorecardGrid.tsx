"use client";

import type { FillerOccurrence, PauseOccurrence, Scorecard, WordTimestamp } from "@/lib/types";
import { SketchBox } from "@/components/sketch/Sketch";
import { Doodle } from "@/components/sketch/Doodle";
import { TranscriptView } from "@/components/TranscriptView";
import { ScorecardTransparency } from "@/components/ScorecardTransparency";

function scoreColor(score: number): string {
  return score >= 3.5 ? "var(--echo)" : "var(--amber)";
}

const RUBRIC_LABELS: Record<string, string> = {
  technical: "technical · explaining a solution",
  project: "technical · project deep-dive",
  system_design: "technical · system design",
  experience: "behavioral · experience story (STAR)",
  introspection: "behavioral · self-reflection & fit",
  learning: "behavioral · learning & curiosity",
};

// Full-bleed grid of per-dimension scorecards with the final score up top.
// `footer` carries the action buttons (retry / new / model answer).
export function ScorecardGrid({
  scorecard,
  footer,
  transcript,
}: {
  scorecard: Scorecard;
  footer?: React.ReactNode;
  transcript?: {
    words: WordTimestamp[];
    transcriptText?: string;
    pauses?: PauseOccurrence[];
    fillers?: FillerOccurrence[];
  };
}) {
  const tilts = ["l", "r", null] as const;
  return (
    <div className="w-full space-y-8">
      {/* Final score header */}
      <div className="flex flex-col items-center text-center gap-3">
        <p className="eyebrow">{RUBRIC_LABELS[scorecard.rubric] ?? "your answer"}</p>
        <div
          className="wobble sketch-shadow flex h-32 w-32 flex-col items-center justify-center"
          style={{ background: "var(--surface)", border: `3px solid ${scoreColor(scorecard.overall_score)}` }}
        >
          <span className="hand text-5xl font-bold" style={{ color: scoreColor(scorecard.overall_score) }}>
            {scorecard.overall_score.toFixed(1)}
          </span>
          <span className="text-xs text-muted">/ 5</span>
        </div>
        <div className="relative inline-block">
          <h2 className="hand text-3xl font-bold">Your Scorecard</h2>
          <Doodle name="squiggle" className="text-amber absolute -bottom-3 left-1/2 -translate-x-1/2" width={160} />
        </div>
        {scorecard.overall_summary && (
          <p className="text-muted text-sm max-w-3xl mt-2">{scorecard.overall_summary}</p>
        )}
      </div>

      <ScorecardTransparency scorecard={scorecard} />

      {/* Dimension cards — full-width grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {scorecard.dimensions.map((d, i) => (
          <SketchBox key={d.dimension} tilt={tilts[i % 3]} className="flex flex-col gap-3">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold leading-tight">{d.dimension}</h3>
              <span
                className="hand text-2xl font-bold tabular-nums shrink-0"
                style={{ color: scoreColor(d.score) }}
              >
                {d.score.toFixed(1)}
              </span>
            </div>
            {d.rationale && <p className="text-sm leading-relaxed">{d.rationale}</p>}
            {d.evidence && (
              <p className="text-xs text-muted italic border-l-2 pl-2" style={{ borderColor: "var(--border)" }}>
                “{d.evidence}”
              </p>
            )}
            {d.suggestion && (
              <p className="text-xs" style={{ color: "var(--echo)" }}>
                → {d.suggestion}
              </p>
            )}
          </SketchBox>
        ))}
      </div>

      {transcript && (
        <TranscriptView
          words={transcript.words}
          fillerIndices={new Set((transcript.fillers ?? []).map((f) => f.index))}
          fillers={transcript.fillers}
          pauses={transcript.pauses}
          transcriptText={transcript.transcriptText}
          evidenceQuotes={scorecard.dimensions.map((d) => d.evidence).filter((e) => e.trim())}
          label="Transcript"
        />
      )}

      {footer && <div className="pt-2">{footer}</div>}
    </div>
  );
}
