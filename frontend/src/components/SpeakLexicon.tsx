"use client";

import type { SessionResult } from "@/lib/types";
import { SketchBox, SketchBar } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { Doodle } from "@/components/sketch/Doodle";
import { FillerBreakdown } from "@/components/MetricCard";
import { TranscriptView } from "@/components/TranscriptView";
import { TAG_ORDER, tagLabel } from "@/lib/tags";

const TAG_MEANING: Record<string, string> = {
  idea_transition: "You reach for a filler while constructing or switching to a new idea.",
  topic_mention: "Fillers cluster around a specific subject you're introducing or naming.",
  hesitation: "You stall to search for a word or recall a fact.",
};

function Stat({ value, label }: { value: string | number; label: string }) {
  return (
    <SketchBox padding={16} className="text-center">
      <p className="hand text-3xl font-bold text-echo tabular-nums">{value}</p>
      <p className="text-xs text-muted mt-1">{label}</p>
    </SketchBox>
  );
}

export function SpeakLexicon({
  session,
  onNext,
}: {
  session: SessionResult;
  onNext: () => void;
}) {
  const m = session.metrics;
  const fillerIndices = new Set(session.fillers.map((f) => f.index));
  const positions = m.position_breakdown;
  const tagEntries = TAG_ORDER.map(
    (t) => [t, m.tag_breakdown?.[t] ?? 0] as const
  ).filter(([, c]) => c > 0);
  const tagMax = Math.max(1, ...tagEntries.map(([, c]) => c));
  // A few concrete "moments" — fillers the model attributed to a reason.
  const moments = session.fillers.filter((f) => f.tag && f.tag_reason).slice(0, 3);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <div className="relative inline-block">
          <h2 className="hand text-4xl font-bold">Speak Lexicon</h2>
          <Doodle name="underline" className="text-echo absolute -bottom-2 left-0" width={200} draw />
        </div>
        <p className="text-muted text-sm mt-4">
          How you actually sounded — the words you lean on, and when.
        </p>
      </div>

      {/* How much */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat value={m.total_fillers} label="filler words" />
        <Stat value={m.fillers_per_minute} label="fillers / min" />
        <Stat value={m.words_per_minute} label="words / min" />
        <Stat value={`${m.avg_pause_sec}s`} label="avg pause" />
      </div>

      {/* Which words */}
      <FillerBreakdown breakdown={m.filler_breakdown} />

      {/* Where they occurred */}
      <SketchBox className="space-y-4">
        <h3 className="hand text-xl font-bold">Where they land</h3>
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
        <p className="text-xs text-muted">
          Highlighted below: fillers <span className="filler-word">like&nbsp;this</span> and pauses{" "}
          <span className="mono text-echo">⏸</span> in your own words.
        </p>
        <TranscriptView
          words={session.words}
          fillerIndices={fillerIndices}
          fillers={session.fillers}
          pauses={session.pauses}
          transcriptText={session.transcript_text}
          label="Your answer"
        />
      </SketchBox>

      {/* What ideas they attach to */}
      <SketchBox className="space-y-4" accent>
        <h3 className="hand text-xl font-bold">What they attach to</h3>
        <p className="text-sm text-muted">
          The moments that trigger your fillers — patterns the AI found in your delivery.
        </p>
        {tagEntries.length === 0 ? (
          <p className="text-sm text-muted">
            No clear pattern — your fillers don&rsquo;t cluster around transitions or topics.
          </p>
        ) : (
          <div className="space-y-4">
            {tagEntries.map(([tag, count]) => (
              <div key={tag}>
                <div className="flex items-center gap-3">
                  <span className="w-28 sm:w-48 text-sm">{tagLabel(tag)}</span>
                  <div className="flex-1">
                    <SketchBar value={count} max={tagMax} height={14} />
                  </div>
                  <span className="text-sm font-medium tabular-nums w-6 text-right">{count}</span>
                </div>
                <p className="text-xs text-muted mt-1 md:ml-52">{TAG_MEANING[tag]}</p>
              </div>
            ))}
          </div>
        )}
        {moments.length > 0 && (
          <div className="space-y-2 pt-2">
            <p className="eyebrow">moments</p>
            {moments.map((f, i) => (
              <div key={i} className="panel-2 p-3 text-sm">
                <span className="filler-word">{f.word}</span>{" "}
                <span className="text-muted">— {f.tag_reason}</span>
              </div>
            ))}
          </div>
        )}
      </SketchBox>

      <div className="flex justify-center pt-2">
        <SketchButton hand onClick={onNext} style={{ fontSize: "1.2rem", padding: "0.8rem 2rem" }}>
          Next: your scorecard →
        </SketchButton>
      </div>
    </div>
  );
}
