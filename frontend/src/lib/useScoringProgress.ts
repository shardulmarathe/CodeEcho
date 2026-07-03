"use client";

import { useEffect, useRef, useState } from "react";

const DEFAULT_EXPECTED_MS = 28_000;
const PROGRESS_CAP = 92;
const FINISH_MS = 700;
const HOLD_AT_100_MS = 350;

export interface ScoringProgressState {
  progress: number;
  phaseLabel: string;
  ready: boolean;
}

function phaseForProgress(progress: number, finishing: boolean): string {
  if (finishing || progress >= 100) return "Done";
  if (progress < 25) return "Pulling coaching context...";
  if (progress < 60) return "Evaluating your answer...";
  if (progress < PROGRESS_CAP) return "Building your scorecard...";
  return "Almost there...";
}

function estimateProgress(elapsedMs: number, expectedMs: number): number {
  const t = Math.max(0, Math.min(1, elapsedMs / expectedMs));
  const eased = 1 - Math.pow(1 - t, 2.2);
  return Math.min(PROGRESS_CAP, eased * PROGRESS_CAP);
}

export function useScoringProgress({
  isActive,
  isComplete,
  startedAt,
  expectedMs = DEFAULT_EXPECTED_MS,
  onReady,
}: {
  isActive: boolean;
  isComplete: boolean;
  startedAt: number | null;
  expectedMs?: number;
  onReady?: () => void;
}): ScoringProgressState {
  const [progress, setProgress] = useState(0);
  const [ready, setReady] = useState(false);
  const progressRef = useRef(0);
  const finishingRef = useRef(false);
  const onReadyRef = useRef(onReady);
  const holdTimerRef = useRef<number | null>(null);
  onReadyRef.current = onReady;

  useEffect(() => {
    return () => {
      if (holdTimerRef.current !== null) {
        window.clearTimeout(holdTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    progressRef.current = progress;
  }, [progress]);

  useEffect(() => {
    if (!isActive && !isComplete) {
      finishingRef.current = false;
      setReady(false);
      setProgress(0);
      progressRef.current = 0;
      return;
    }

    if (!isComplete) {
      finishingRef.current = false;
      if (!isActive || startedAt === null) return;

      const tick = () => {
        const next = estimateProgress(Date.now() - startedAt, expectedMs);
        setProgress((current) => {
          const value = Math.max(current, next);
          progressRef.current = value;
          return value;
        });
      };

      tick();
      const interval = window.setInterval(tick, 200);
      return () => window.clearInterval(interval);
    }

    if (finishingRef.current) return;
    finishingRef.current = true;

    const estimated =
      startedAt !== null ? estimateProgress(Date.now() - startedAt, expectedMs) : progressRef.current;
    const from = Math.max(progressRef.current, estimated);
    setProgress(from);
    progressRef.current = from;

    const start = performance.now();

    const animate = (now: number) => {
      const t = Math.min(1, (now - start) / FINISH_MS);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = from + (100 - from) * eased;
      setProgress(value);
      progressRef.current = value;

      if (t < 1) {
        requestAnimationFrame(animate);
      } else {
        setProgress(100);
        progressRef.current = 100;
        setReady(true);
        holdTimerRef.current = window.setTimeout(() => {
          holdTimerRef.current = null;
          onReadyRef.current?.();
        }, HOLD_AT_100_MS);
      }
    };

    requestAnimationFrame(animate);
  }, [expectedMs, isActive, isComplete, startedAt]);

  const finishing = isComplete && !ready;

  return {
    progress,
    phaseLabel: phaseForProgress(progress, finishing),
    ready,
  };
}
