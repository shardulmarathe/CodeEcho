"use client";

import { useState } from "react";
import type { Question } from "@/lib/types";
import { generateQuestion, submitQuestion } from "@/lib/api";
import { CircleChoice } from "@/components/sketch/CircleChoice";
import { SketchButton } from "@/components/sketch/SketchButton";
import { SketchBox } from "@/components/sketch/Sketch";

type QType = "behavioral" | "technical" | "custom";

const TYPES = [
  { v: "behavioral", title: "Behavioral", desc: "STAR, strengths, motivation" },
  { v: "technical", title: "Technical", desc: "Coding, project, or design" },
  { v: "custom", title: "Bring Your Own", desc: "Paste any question" },
];
const TRACKS = [
  { v: "coding", title: "Coding", desc: "Algorithms & data structures" },
  { v: "project", title: "Project", desc: "Deep-dive a project you built" },
  { v: "system_design", title: "System Design", desc: "Design at scale" },
];
const LEVELS = [
  { v: "intern", title: "Intern" },
  { v: "new-grad", title: "New grad" },
  { v: "mid", title: "Mid-level" },
  { v: "senior", title: "Senior" },
];

export function QuestionSetup({
  onReady,
  disabled,
}: {
  onReady: (q: Question) => void;
  disabled?: boolean;
}) {
  const [qtype, setQtype] = useState<QType | null>(null);
  const [track, setTrack] = useState("coding");
  const [seniority, setSeniority] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const busy = disabled || loading;
  const ready =
    !!qtype &&
    !!seniority &&
    (qtype !== "custom" || custom.trim().length > 3);

  const run = async () => {
    if (!ready || !qtype) return;
    setLoading(true);
    setError(null);
    try {
      const q =
        qtype === "custom"
          ? await submitQuestion({ qtype: "behavioral", prompt: custom, meta: { seniority } })
          : await generateQuestion({
              qtype,
              role: "Software Engineer",
              seniority: seniority!,
              track: qtype === "technical" ? track : undefined,
            });
      onReady(q);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-10 py-4 w-full">
      {/* Question type — three on one line */}
      <div className="flex flex-col items-center gap-4">
        <p className="eyebrow">what do you want to practice?</p>
        <div className="flex flex-wrap justify-center gap-10">
          {TYPES.map((t) => (
            <CircleChoice
              key={t.v}
              title={t.title}
              desc={t.desc}
              size={200}
              selected={qtype === t.v}
              onPick={() => setQtype(t.v as QType)}
            />
          ))}
        </div>
      </div>

      {/* Technical → which track (circles) */}
      {qtype === "technical" && (
        <div className="flex flex-col items-center gap-4">
          <p className="eyebrow">what kind?</p>
          <div className="flex flex-wrap justify-center gap-8">
            {TRACKS.map((t) => (
              <CircleChoice
                key={t.v}
                title={t.title}
                desc={t.desc}
                size={172}
                selected={track === t.v}
                onPick={() => setTrack(t.v)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Paste your own → sketch box */}
      {qtype === "custom" && (
        <div className="w-full max-w-2xl space-y-2">
          <p className="eyebrow text-center">your question</p>
          <SketchBox padding={4}>
            <textarea
              value={custom}
              onChange={(e) => setCustom(e.target.value)}
              disabled={busy}
              rows={5}
              placeholder="Paste any interview question — coding or behavioral. We'll detect which it is."
              className="w-full p-4 text-base bg-transparent resize-none focus:outline-none"
              style={{ border: "none" }}
            />
          </SketchBox>
        </div>
      )}

      {/* Who are you? */}
      <div className="flex flex-col items-center gap-4">
        <p className="eyebrow">who are you?</p>
        <div className="flex flex-wrap justify-center gap-8">
          {LEVELS.map((l) => (
            <CircleChoice
              key={l.v}
              title={l.title}
              size={144}
              selected={seniority === l.v}
              onPick={() => setSeniority(l.v)}
            />
          ))}
        </div>
      </div>

      <SketchButton hand disabled={!ready || busy} onClick={run} style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}>
        {loading ? "Working…" : qtype === "custom" ? "Use this question" : "Generate a question"}
      </SketchButton>

      {error && <p className="text-sm" style={{ color: "#f87171" }}>{error}</p>}
    </div>
  );
}
