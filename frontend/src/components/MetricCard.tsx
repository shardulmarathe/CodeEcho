"use client";

import { SketchBox, SketchBar } from "./sketch/Sketch";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
}

export function MetricCard({ label, value, unit }: MetricCardProps) {
  return (
    <SketchBox className="flex flex-col items-center gap-2 text-center" padding={16}>
      <div className="metric-ring">
        <span className="text-xl font-bold tabular-nums">
          {value}
          {unit && <span className="text-sm font-normal text-neutral-500">{unit}</span>}
        </span>
      </div>
      <p className="text-sm text-neutral-500">{label}</p>
    </SketchBox>
  );
}

interface FillerBreakdownProps {
  breakdown: Record<string, number>;
}

export function FillerBreakdown({ breakdown }: FillerBreakdownProps) {
  const entries = Object.entries(breakdown).sort((a, b) => b[1] - a[1]);
  const max = entries[0]?.[1] ?? 1;

  return (
    <SketchBox className="space-y-3">
      <h3 className="font-semibold">Filler Breakdown</h3>
      {entries.length === 0 ? (
        <p className="text-sm text-neutral-500">No fillers detected</p>
      ) : (
        entries.map(([word, count]) => (
          <div key={word} className="flex items-center gap-3">
            <span className="w-20 text-sm capitalize">{word}</span>
            <div className="flex-1">
              <SketchBar value={count} max={max} height={12} />
            </div>
            <span className="text-sm font-medium tabular-nums w-6 text-right">{count}</span>
          </div>
        ))
      )}
    </SketchBox>
  );
}
