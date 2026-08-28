"use client";

import { useEffect, useState } from "react";
import { getMe, startInterview } from "@/lib/api";
import type {
  InterviewMode,
  InterviewQuestionResponse,
  TechnicalSection,
} from "@/lib/types";
import { CircleChoice } from "@/components/sketch/CircleChoice";
import { SketchButton } from "@/components/sketch/SketchButton";
import { SketchWaveform } from "@/components/sketch/SketchWaveform";

const TYPES = [
  { v: "behavioral", title: "Behavioral", desc: "Experience, fit & learning" },
  { v: "technical", title: "Technical", desc: "Coding, system design, or a project" },
];
const SECTIONS = [
  { v: "coding", title: "Coding", desc: "2–3 problems, easy → hard" },
  { v: "system_design", title: "System Design", desc: "One design, deep follow-ups" },
  { v: "project", title: "Project", desc: "One project, deep follow-ups" },
];
const LEVELS = [
  { v: "intern", title: "Intern" },
  { v: "new-grad", title: "New grad" },
  { v: "mid", title: "Mid-level" },
  { v: "senior", title: "Senior" },
];

export function InterviewSetup({
  onStarted,
}: {
  onStarted: (r: InterviewQuestionResponse) => void;
}) {
  const [mode, setMode] = useState<InterviewMode | null>(null);
  const [section, setSection] = useState<TechnicalSection | null>(null);
  const [seniority, setSeniority] = useState<string | null>(null);
  const [role, setRole] = useState("Software Engineer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then((me) => {
        if (me.profile?.seniority) setSeniority(me.profile.seniority);
        if (me.profile?.target_role) setRole(me.profile.target_role);
      })
      .catch(() => {});
  }, []);

  const ready = mode && seniority && (mode !== "technical" || section);

  const begin = async () => {
    if (!ready || !mode) return;
    setLoading(true);
    setError(null);
    try {
      const r = await startInterview({
        mode,
        section: mode === "technical" ? section ?? "coding" : undefined,
        role,
        seniority: seniority!,
        num_behavioral: 3,
      });
      onStarted(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the interview");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-4 py-16">
        <SketchWaveform bars={30} height={56} />
        <p className="hand text-2xl">Setting up your interview…</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-10 py-4 w-full">
      {/* Interview type */}
      <div className="flex flex-col items-center gap-4">
        <p className="eyebrow">interview type</p>
        <div className="flex flex-wrap justify-center gap-12">
          {TYPES.map((t) => (
            <CircleChoice
              key={t.v}
              title={t.title}
              desc={t.desc}
              size={230}
              selected={mode === t.v}
              onPick={() => {
                setMode(t.v as InterviewMode);
                if (t.v !== "technical") setSection(null);
              }}
            />
          ))}
        </div>
      </div>

      {/* Section — only for technical */}
      {mode === "technical" && (
        <div className="flex flex-col items-center gap-4">
          <p className="eyebrow">which section?</p>
          <div className="flex flex-wrap justify-center gap-10">
            {SECTIONS.map((s) => (
              <CircleChoice
                key={s.v}
                title={s.title}
                desc={s.desc}
                size={190}
                selected={section === s.v}
                onPick={() => setSection(s.v as TechnicalSection)}
              />
            ))}
          </div>
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
              size={148}
              selected={seniority === l.v}
              onPick={() => setSeniority(l.v)}
            />
          ))}
        </div>
      </div>

      <SketchButton hand disabled={!ready} onClick={begin} style={{ fontSize: "1.3rem", padding: "0.9rem 2.6rem" }}>
        Start interview
      </SketchButton>

      {error && <p className="text-sm" style={{ color: "#f87171" }}>{error}</p>}
    </div>
  );
}
