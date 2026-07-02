"use client";

import { useState } from "react";
import type { InterviewReport as Report, Scorecard } from "@/lib/types";
import { scoreAttempt } from "@/lib/api";
import { ScorecardView } from "@/components/ScorecardView";
import { SketchBox } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";
import { Doodle } from "@/components/sketch/Doodle";

function scoreColor(score: number): string {
  return score >= 3.5 ? "var(--fg)" : "var(--amber)";
}

function List({ title, items, accent }: { title: string; items: string[]; accent: string }) {
  if (!items.length) return null;
  return (
    <SketchBox className="space-y-3">
      <p className="eyebrow">{title}</p>
      <ul className="space-y-2">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm">
            <span style={{ color: accent }}>›</span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </SketchBox>
  );
}

export function InterviewReport({
  report,
  onRestart,
}: {
  report: Report;
  onRestart: () => void;
}) {
  const [showDetail, setShowDetail] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  // per-question scorecards, fetched on demand
  const [cards, setCards] = useState<Record<string, Scorecard | "loading" | "error">>({});

  const general = report.general_scorecard;
  const mains = report.turns.filter((t) => !t.is_followup).length;
  const followups = report.turns.length - mains;
  const tilts = ["l", "r", null] as const;

  const openTurn = async (turnId: string, attemptId?: string | null) => {
    if (open === turnId) {
      setOpen(null);
      return;
    }
    setOpen(turnId);
    if (attemptId && !cards[turnId]) {
      setCards((c) => ({ ...c, [turnId]: "loading" }));
      try {
        const sc = await scoreAttempt(attemptId);
        setCards((c) => ({ ...c, [turnId]: sc }));
      } catch {
        setCards((c) => ({ ...c, [turnId]: "error" }));
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Final score header */}
      <div className="flex flex-col items-center text-center gap-3">
        <p className="eyebrow">interview report</p>
        <div
          className="wobble sketch-shadow flex h-32 w-32 flex-col items-center justify-center"
          style={{ background: "var(--surface)", border: `3px solid ${scoreColor(report.overall_score)}` }}
        >
          <span className="hand text-5xl font-bold" style={{ color: scoreColor(report.overall_score) }}>
            {report.overall_score.toFixed(1)}
          </span>
          <span className="text-xs text-muted">/ 5</span>
        </div>
        {report.verdict && (
          <span
            className="hand text-xl capitalize px-4 py-1"
            style={{ background: "var(--amber)", color: "#1a1206", borderRadius: "9px 13px 9px 13px" }}
          >
            {report.verdict}
          </span>
        )}
        <div className="relative inline-block mt-1">
          <h2 className="hand text-3xl font-bold">How you did</h2>
          <Doodle name="underline" className="text-amber absolute -bottom-2 left-0" width={180} draw />
        </div>
        {report.summary && <p className="text-muted text-sm max-w-3xl mt-2">{report.summary}</p>}
      </div>

      {/* Aggregate delivery */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Questions", value: `${mains} + ${followups}` },
          { label: "Total fillers", value: report.total_fillers },
          { label: "Avg words / min", value: report.avg_words_per_minute },
          { label: "Pauses", value: report.total_pauses },
        ].map((m) => (
          <SketchBox key={m.label} padding={16} className="text-center">
            <p className="hand text-3xl font-bold tabular-nums">{m.value}</p>
            <p className="text-xs text-muted mt-1">{m.label}</p>
          </SketchBox>
        ))}
      </div>

      {/* Generalized rubric — one scorecard for the whole interview */}
      {general && general.dimensions.length > 0 && (
        <div className="space-y-3">
          <p className="eyebrow">overall rubric</p>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {general.dimensions.map((d, i) => (
              <SketchBox key={d.dimension} tilt={tilts[i % 3]} className="flex flex-col gap-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold leading-tight">{d.dimension}</h3>
                  <span className="hand text-2xl font-bold tabular-nums shrink-0" style={{ color: scoreColor(d.score) }}>
                    {d.score.toFixed(1)}
                  </span>
                </div>
                {d.rationale && <p className="text-sm leading-relaxed">{d.rationale}</p>}
                {d.suggestion && <p className="text-xs" style={{ color: "var(--fg)" }}>→ {d.suggestion}</p>}
              </SketchBox>
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        <List title="strengths" items={report.strengths} accent="var(--fg)" />
        <List title="focus on next" items={report.improvements} accent="var(--amber)" />
      </div>

      {report.followup_handling && (
        <SketchBox className="space-y-2" accent>
          <p className="eyebrow">handling follow-ups</p>
          <p className="text-sm leading-relaxed">{report.followup_handling}</p>
        </SketchBox>
      )}

      {/* Per-question feedback — on demand */}
      <div className="flex flex-col items-center gap-4 pt-2">
        <SketchButton variant="ghost" onClick={() => setShowDetail((s) => !s)}>
          {showDetail ? "Hide per-question feedback" : "See feedback per question"}
        </SketchButton>

        {showDetail && (
          <div className="w-full space-y-3">
            <p className="eyebrow text-center">pick a question for its full scorecard</p>
            {report.turns.map((t) => (
              <SketchBox key={t.turn_id} padding={0}>
                <button
                  onClick={() => openTurn(t.turn_id, t.attempt_id)}
                  className="w-full flex items-center gap-3 p-4 text-left cursor-pointer"
                >
                  <span
                    className="px-2 py-0.5 text-[10px] font-medium shrink-0"
                    style={{ background: "var(--surface-2)", color: "var(--muted)", border: "1px solid var(--border)", borderRadius: "8px 12px 8px 12px" }}
                  >
                    {t.is_followup ? "follow-up" : "main"}
                  </span>
                  <span className="flex-1 text-sm">{t.question}</span>
                  <span className="mono text-xs text-muted shrink-0">{open === t.turn_id ? "−" : "+"}</span>
                </button>
                {open === t.turn_id && (
                  <div className="p-4 pt-0">
                    {cards[t.turn_id] === "loading" && (
                      <p className="text-sm text-muted">Scoring this answer…</p>
                    )}
                    {cards[t.turn_id] === "error" && (
                      <p className="text-sm" style={{ color: "#f87171" }}>Couldn&rsquo;t score this one.</p>
                    )}
                    {cards[t.turn_id] && cards[t.turn_id] !== "loading" && cards[t.turn_id] !== "error" && (
                      <ScorecardView scorecard={cards[t.turn_id] as Scorecard} />
                    )}
                  </div>
                )}
              </SketchBox>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-center pt-2">
        <SketchButton hand onClick={onRestart} style={{ fontSize: "1.1rem" }}>
          New interview
        </SketchButton>
      </div>
    </div>
  );
}
