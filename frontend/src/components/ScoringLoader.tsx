"use client";

import { useEffect, useState } from "react";

import { SketchBar, SketchBox } from "@/components/sketch/Sketch";
import { pickRandomTip, rotateTip, type InterviewTip } from "@/lib/interviewTips";
import { useScoringProgress } from "@/lib/useScoringProgress";

const TIP_INTERVAL_MS = 3_000;

export function ScoringLoader({
  active,
  complete = false,
  startedAt,
  onReady,
  size = "default",
}: {
  active: boolean;
  complete?: boolean;
  startedAt: number | null;
  onReady?: () => void;
  size?: "default" | "compact";
}) {
  const { progress, phaseLabel } = useScoringProgress({
    isActive: active,
    isComplete: complete,
    startedAt,
    onReady,
  });
  const [tip, setTip] = useState<InterviewTip>(() => pickRandomTip());
  const [tipVisible, setTipVisible] = useState(true);
  const compact = size === "compact";

  useEffect(() => {
    if (!active || complete) return;

    const interval = window.setInterval(() => {
      setTipVisible(false);
      window.setTimeout(() => {
        setTip((current) => rotateTip(current.id));
        setTipVisible(true);
      }, 200);
    }, TIP_INTERVAL_MS);

    return () => window.clearInterval(interval);
  }, [active, complete]);

  return (
    <SketchBox
      padding={compact ? 16 : 24}
      className={compact ? "space-y-3" : "max-w-xl mx-auto space-y-5"}
    >
      <div className="space-y-1 text-center">
        <p className={compact ? "hand text-lg font-bold" : "hand text-2xl font-bold"}>
          Scoring your answer
        </p>
        {!compact && (
          <p className="text-sm text-muted">This usually takes 15-30 seconds.</p>
        )}
      </div>

      <div className="space-y-2">
        <SketchBar value={progress} height={compact ? 10 : 12} color="var(--echo)" smooth={false} />
        <div className="flex items-center justify-between gap-3 text-xs mono text-muted">
          <span>{phaseLabel}</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>

      <p
        className={`text-sm text-muted leading-relaxed text-center transition-opacity duration-200 ${
          tipVisible ? "opacity-100" : "opacity-0"
        }`}
      >
        <span className="text-echo font-medium">{tip.title}.</span> {tip.body}
      </p>
    </SketchBox>
  );
}
