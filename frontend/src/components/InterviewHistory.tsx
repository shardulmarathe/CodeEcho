"use client";

import { useEffect, useState } from "react";
import { listInterviews } from "@/lib/api";
import type { InterviewSession } from "@/lib/types";
import { SketchBox, SketchPill } from "@/components/sketch/Sketch";
import { SketchButton } from "@/components/sketch/SketchButton";

const MAX_SHOWN = 5;

const SECTION_LABELS: Record<string, string> = {
  coding: "Coding",
  system_design: "System design",
  project: "Project",
};

function label(s: InterviewSession): string {
  if (s.mode !== "technical") return "Behavioral";
  const section = typeof s.config?.section === "string" ? s.config.section : "";
  return SECTION_LABELS[section] ?? "Technical";
}

function formatDate(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const thisYear = d.getFullYear() === new Date().getFullYear();
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: thisYear ? undefined : "numeric",
  });
}

/** How far in. Follow-ups are excluded from the count: the plan is the set of MAIN
 *  questions, so counting probes would make "3 of 3" arrive early and then overflow. */
function progressLabel(s: InterviewSession): string {
  const total = s.plan?.length ?? 0;
  const mainsAnswered = s.turns.filter((t) => !t.is_followup && t.answered).length;
  if (!total) return `${mainsAnswered} answered`;
  return `${Math.min(mainsAnswered, total)} of ${total} answered`;
}

function isResumable(s: InterviewSession): boolean {
  return s.status !== "complete" && s.turns.some((t) => !t.answered);
}

/** Past interviews, on the setup screen. Renders nothing until there is something
 *  worth showing, so a first-time user sees the plain setup flow. */
export function InterviewHistory({
  onResume,
  onViewReport,
  disabled,
}: {
  onResume: (s: InterviewSession) => void;
  onViewReport: (s: InterviewSession) => void;
  disabled?: boolean;
}) {
  const [sessions, setSessions] = useState<InterviewSession[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    listInterviews()
      .then((rows) => {
        if (!cancelled) setSessions(rows);
      })
      // A history panel is never worth blocking the setup flow over.
      .catch(() => {
        if (!cancelled) setSessions([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const shown = (sessions ?? []).filter(
    (s) => isResumable(s) || s.status === "complete"
  );
  if (!shown.length) return null;

  return (
    <div className="w-full max-w-2xl flex flex-col items-center gap-4">
      <p className="eyebrow">your interviews</p>
      <SketchBox className="w-full space-y-0" padding={8}>
        {shown.slice(0, MAX_SHOWN).map((s, i) => {
          const resumable = isResumable(s);
          const score = s.report?.overall_score;
          return (
            <div
              key={s.session_id}
              className="flex items-center justify-between gap-4 px-4 py-3"
              style={i > 0 ? { borderTop: "1.5px solid var(--border)" } : undefined}
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{label(s)}</span>
                  <SketchPill>{resumable ? "in progress" : "complete"}</SketchPill>
                </div>
                <p className="text-xs text-muted mt-1">
                  {[formatDate(s.created_at), progressLabel(s)]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {!resumable && score != null && score > 0 && (
                  <span className="hand text-2xl font-bold tabular-nums">
                    {score.toFixed(1)}
                  </span>
                )}
                <SketchButton
                  variant="ghost"
                  disabled={disabled}
                  onClick={() => (resumable ? onResume(s) : onViewReport(s))}
                >
                  {resumable ? "Resume" : "Report"}
                </SketchButton>
              </div>
            </div>
          );
        })}
      </SketchBox>
    </div>
  );
}
