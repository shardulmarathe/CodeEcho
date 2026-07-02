"use client";

import type { ModelAnswer } from "@/lib/types";

export function ModelAnswerPanel({ answer }: { answer: ModelAnswer }) {
  const isTech = answer.rubric === "technical";
  return (
    <div className="panel p-5 space-y-4" style={{ borderColor: "var(--echo)" }}>
      <p className="eyebrow" style={{ color: "var(--echo)" }}>
        model answer
      </p>

      {isTech ? (
        <>
          {answer.approach && (
            <div>
              <p className="text-sm font-semibold">Optimal approach</p>
              <p className="text-sm text-muted mt-1 leading-relaxed">{answer.approach}</p>
            </div>
          )}
          {answer.complexity && (
            <div>
              <p className="text-sm font-semibold">Complexity</p>
              <p className="text-sm mono text-echo mt-1">{answer.complexity}</p>
            </div>
          )}
        </>
      ) : (
        answer.outline && (
          <div>
            <p className="text-sm font-semibold">How to structure it</p>
            <p className="text-sm text-muted mt-1 leading-relaxed">{answer.outline}</p>
          </div>
        )
      )}

      {answer.key_points.length > 0 && (
        <div>
          <p className="text-sm font-semibold mb-1.5">What a 5/5 covers</p>
          <ul className="space-y-1.5">
            {answer.key_points.map((p, i) => (
              <li key={i} className="flex gap-2 text-sm text-muted">
                <span className="text-echo shrink-0">·</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
