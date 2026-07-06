"use client";

import type { Question } from "@/lib/types";

export function ProblemPanel({ question }: { question: Question }) {
  const isTech = question.qtype === "technical";
  return (
    <div className="panel p-5 space-y-4">
      <p className="font-medium text-base sm:text-lg leading-relaxed break-words">{question.prompt}</p>

      {isTech && question.constraints && (
        <div>
          <p className="eyebrow mb-1">constraints</p>
          <p className="text-sm text-muted">{question.constraints}</p>
        </div>
      )}

      {isTech && question.examples.length > 0 && (
        <div className="space-y-2">
          <p className="eyebrow mb-1">examples</p>
          {question.examples.map((e, i) => (
            <div key={i} className="panel-2 p-3 text-sm mono space-y-1 break-words">
              <div>
                <span className="text-muted">in&nbsp;&nbsp;</span>
                {e.input}
              </div>
              <div>
                <span className="text-muted">out&nbsp;</span>
                <span className="text-echo">{e.output}</span>
              </div>
              {e.explanation && (
                <div className="text-muted">{"// "}{e.explanation}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
