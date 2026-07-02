"use client";

import type { SessionMetrics } from "@/lib/types";
import { formatDuration } from "@/lib/api";
import { MetricCard, FillerBreakdown } from "./MetricCard";
import { SketchBox, SketchBar } from "./sketch/Sketch";
import { TAG_ORDER, tagLabel } from "@/lib/tags";

interface OverviewTabProps {
  metrics: SessionMetrics;
}

export function OverviewTab({ metrics }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard label="Duration" value={formatDuration(metrics.duration_sec)} />
        <MetricCard label="Total Fillers" value={metrics.total_fillers} />
        <MetricCard label="Fillers / Min" value={metrics.fillers_per_minute} />
        <MetricCard label="Words / Min" value={metrics.words_per_minute} />
        <MetricCard label="Pauses" value={metrics.total_pauses} />
        <MetricCard label="Avg Pause" value={`${metrics.avg_pause_sec}s`} />
      </div>
      <FillerBreakdown breakdown={metrics.filler_breakdown} />
    </div>
  );
}

interface AnalyticsTabProps {
  metrics: SessionMetrics;
}

export function AnalyticsTab({ metrics }: AnalyticsTabProps) {
  const positions = metrics.position_breakdown;
  const tagEntries = TAG_ORDER.map(
    (tag) => [tag, metrics.tag_breakdown?.[tag] ?? 0] as const
  ).filter(([, count]) => count > 0);
  const tagMax = Math.max(1, ...tagEntries.map(([, c]) => c));

  return (
    <div className="space-y-6">
      {/* Sentence Position */}
      <SketchBox className="space-y-4">
        <h3 className="font-semibold">Sentence Position</h3>
        <p className="text-sm text-neutral-500">
          Where fillers occur within sentences
        </p>
        <div className="space-y-3">
          {(["beginning", "middle", "end"] as const).map((pos) => (
            <div key={pos} className="flex items-center gap-3">
              <span className="w-24 text-sm capitalize">{pos}</span>
              <div className="flex-1">
                <SketchBar value={positions[pos]} max={100} height={14} />
              </div>
              <span className="text-sm font-medium tabular-nums w-12 text-right">
                {positions[pos]}%
              </span>
            </div>
          ))}
        </div>
      </SketchBox>

      {/* Why your fillers happen — LLM tags */}
      <SketchBox className="space-y-4">
        <h3 className="font-semibold">Why your fillers happen</h3>
        <p className="text-sm text-neutral-500">
          Patterns detected by AI in when your fillers occur
        </p>
        {tagEntries.length === 0 ? (
          <p className="text-sm text-neutral-500">
            No clear patterns detected — your fillers don&rsquo;t cluster around
            transitions or specific topics.
          </p>
        ) : (
          <div className="space-y-3">
            {tagEntries.map(([tag, count]) => (
              <div key={tag} className="flex items-center gap-3">
                <span className="w-44 text-sm">{tagLabel(tag)}</span>
                <div className="flex-1">
                  <SketchBar value={count} max={tagMax} height={14} />
                </div>
                <span className="text-sm font-medium tabular-nums w-6 text-right">
                  {count}
                </span>
              </div>
            ))}
          </div>
        )}
      </SketchBox>

      {/* Pause Analysis */}
      <SketchBox className="space-y-4">
        <h3 className="font-semibold">Pause Analysis</h3>
        <p className="text-sm text-neutral-500">
          Silent gaps of 0.6s or more in your delivery
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">{metrics.total_pauses}</p>
            <p className="text-xs text-neutral-500 mt-1">Total pauses</p>
          </div>
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">{metrics.long_pauses}</p>
            <p className="text-xs text-neutral-500 mt-1">Long pauses (&ge; 1.5s)</p>
          </div>
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">
              {metrics.pauses_per_minute}
            </p>
            <p className="text-xs text-neutral-500 mt-1">Pauses / min</p>
          </div>
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">
              {metrics.avg_pause_before_filler_sec}s
            </p>
            <p className="text-xs text-neutral-500 mt-1">Avg pause before filler</p>
          </div>
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">
              {metrics.avg_pause_elsewhere_sec}s
            </p>
            <p className="text-xs text-neutral-500 mt-1">Avg pause elsewhere</p>
          </div>
          <div className="rounded-2xl bg-neutral-50 p-4 text-center">
            <p className="text-2xl font-bold tabular-nums">
              {metrics.long_pause_filler_pct}%
            </p>
            <p className="text-xs text-neutral-500 mt-1">Fillers after &gt; 0.8s pause</p>
          </div>
        </div>
      </SketchBox>
    </div>
  );
}

export function HistoryTab() {
  return (
    <SketchBox className="text-center space-y-4" padding={48}>
      <div className="h-16 w-16 rounded-full border-2 border-neutral-200 flex items-center justify-center mx-auto">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 8v4l3 3" />
          <circle cx="12" cy="12" r="10" />
        </svg>
      </div>
      <h3 className="font-semibold">Track Your Progress</h3>
      <p className="text-sm text-neutral-500 max-w-sm mx-auto">
        Create an account to save sessions, view trends over time, compare speeches, and unlock personal bests.
      </p>
      <button className="btn-circle bg-neutral-900 text-white text-sm">
        Sign up to save
      </button>
    </SketchBox>
  );
}
