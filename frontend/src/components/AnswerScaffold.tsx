"use client";

const TECHNICAL_STEPS = [
  "Clarify constraints — input size, types, duplicates, edge conditions",
  "Restate the problem and trace one example out loud",
  "Give the brute-force approach first",
  "Optimize it — and say why the optimization works",
  "State time & space complexity (Big-O)",
  "Call out edge cases — empty, single element, negatives, no answer",
];

const BEHAVIORAL_STEPS = [
  "Situation — set brief, specific context",
  "Task — your exact goal or responsibility",
  "Action — the concrete steps YOU took (not the team)",
  "Result — the outcome, ideally quantified",
  "Tie it back to what the question actually asked",
];

const PROJECT_STEPS = [
  "Context — the problem and why it mattered, briefly",
  "Your role — what YOU personally built or owned (I, not we)",
  "Key technical decisions — the trade-offs you weighed and why",
  "Hardest challenge — and how you worked through it",
  "Impact — the outcome: users, performance, what shipped",
];

const SYSTEM_DESIGN_STEPS = [
  "Clarify requirements — functional, non-functional, and the scale (users, QPS, data)",
  "Sketch the high-level design — core components, APIs, and data flow",
  "Pick the data model & storage — and justify the choice",
  "Deep-dive the key mechanism — e.g. how the surge price is actually computed",
  "Scale it — caching, sharding, load balancing; name the bottlenecks",
  "Call out trade-offs — consistency vs availability, and alternatives you weighed",
];

const STEPS: Record<string, string[]> = {
  technical: TECHNICAL_STEPS,
  project: PROJECT_STEPS,
  system_design: SYSTEM_DESIGN_STEPS,
  behavioral: BEHAVIORAL_STEPS,
};

export function AnswerScaffold({ qtype }: { qtype: string }) {
  const steps = STEPS[qtype] ?? BEHAVIORAL_STEPS;
  return (
    <div className="panel p-5 space-y-3">
      <p className="eyebrow">hint · what a strong answer covers</p>
      <ul className="space-y-2">
        {steps.map((s, i) => (
          <li key={i} className="flex gap-3 text-sm text-muted">
            <span className="mono text-echo shrink-0">{String(i + 1).padStart(2, "0")}</span>
            <span>{s}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
