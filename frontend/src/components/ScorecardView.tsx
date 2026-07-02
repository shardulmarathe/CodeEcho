"use client";

import type { Scorecard } from "@/lib/types";
import { SketchBox, SketchBar } from "./sketch/Sketch";

// Signal scale: teal = strong, amber = needs work.
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

export function ScorecardView({ scorecard }: { scorecard: Scorecard }) {
  const rubricLabel = RUBRIC_LABELS[scorecard.rubric] ?? "behavioral";
  const ringColor = scoreColor(scorecard.overall_score);

  return (
    <SketchBox className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow">{rubricLabel}</p>
          <h3 className="font-display text-lg font-bold mt-1">Scorecard</h3>
          {scorecard.overall_summary && (
            <p className="text-sm text-muted mt-2 max-w-xl leading-relaxed">
              {scorecard.overall_summary}
            </p>
          )}
        </div>
        <div className="text-center shrink-0">
          <div
            className="flex h-20 w-20 items-center justify-center rounded-full border-2"
            style={{ borderColor: ringColor }}
          >
            <span className="font-display text-2xl font-bold tabular-nums" style={{ color: ringColor }}>
              {scorecard.overall_score.toFixed(1)}
            </span>
          </div>
          <p className="text-xs mono text-muted mt-1">overall / 5</p>
        </div>
      </div>

      <div className="space-y-5">
        {scorecard.dimensions.map((d) => (
          <div key={d.dimension} className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{d.dimension}</span>
              <span
                className="text-sm font-semibold tabular-nums mono"
                style={{ color: scoreColor(d.score) }}
              >
                {d.score.toFixed(1)}/5
              </span>
            </div>
            <SketchBar value={d.score} max={5} height={10} color={scoreColor(d.score)} />
            {d.rationale && <p className="text-sm text-muted">{d.rationale}</p>}
            {d.evidence && (
              <p className="text-xs italic" style={{ color: "var(--muted)" }}>
                &ldquo;{d.evidence}&rdquo;
              </p>
            )}
            {d.suggestion && (
              <p className="text-sm text-fg">
                <span className="font-semibold text-echo">Fix: </span>
                {d.suggestion}
              </p>
            )}
          </div>
        ))}
      </div>
    </SketchBox>
  );
}
