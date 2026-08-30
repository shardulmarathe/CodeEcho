import type { Scorecard } from "@/lib/types";

// Frozen, read-only example in the exact scorecard API shape. It is always presented
// with Sample / Worked example chrome and is never treated as a visitor's result.
export const SAMPLE_SCORECARD: Scorecard = {
  attempt_id: "sample-project-scorecard",
  rubric: "project",
  overall_score: 4.0,
  overall_summary:
    "A strong project walkthrough with clear ownership and credible technical trade-offs. The impact is concrete, but the explanation would be stronger with one baseline metric and a tighter opening.",
  dimensions: [
    {
      dimension: "Context",
      score: 3.5,
      rationale: "The problem and users are clear, though the setup takes longer than needed.",
      evidence: "Support engineers were spending about six hours a week tracing failed jobs.",
      suggestion: "Open with the user problem and scale in two sentences, then move to your role.",
    },
    {
      dimension: "Your contribution",
      score: 4.5,
      rationale: "Individual ownership is specific from design through rollout.",
      evidence: "I designed the event schema, built the ingestion worker, and led the staged rollout.",
      suggestion: "Name one decision you delegated to show how you worked with the rest of the team.",
    },
    {
      dimension: "Technical depth",
      score: 4.0,
      rationale: "The answer explains the queueing choice and failure-handling trade-off with useful detail.",
      evidence: "We chose at-least-once delivery and made each consumer idempotent with an event key.",
      suggestion: "Briefly explain why exactly-once semantics were not worth the added complexity here.",
    },
    {
      dimension: "Impact",
      score: 4.5,
      rationale: "The result connects the implementation to measurable operational improvement.",
      evidence: "Debugging time dropped from hours to under twenty minutes for most incidents.",
      suggestion: "Add the before-and-after failure-detection time to make the impact even sharper.",
    },
    {
      dimension: "Relevance",
      score: 4.0,
      rationale: "The example demonstrates backend design, ownership, and production judgment.",
      evidence: "The rollout covered twelve services without changing their existing job contracts.",
      suggestion: "Close by tying the project directly to the role's reliability requirements.",
    },
    {
      dimension: "Conciseness",
      score: 3.5,
      rationale: "The arc is easy to follow, but some implementation history can be trimmed.",
      evidence: "We first considered polling, then webhooks, and then moved to the event bus.",
      suggestion: "Keep the rejected alternatives to one sentence focused on the decisive trade-off.",
    },
    {
      dimension: "Delivery",
      score: 4.0,
      rationale: "The explanation is confident and structured with only minor hesitation.",
      evidence: "The key constraint was preserving compatibility while we migrated incrementally.",
      suggestion: "Pause after the architecture summary before moving into implementation details.",
    },
  ],
  sources: [],
  dimension_definitions: [
    { name: "Context", description: "did they explain the problem and why it mattered, briefly?" },
    {
      name: "Your contribution",
      description: "is their specific role and what they personally built clear?",
    },
    {
      name: "Technical depth",
      description: "did they surface real decisions, trade-offs, and challenges?",
    },
    {
      name: "Impact",
      description: "is there a concrete outcome such as users, performance, or what shipped?",
    },
    {
      name: "Relevance",
      description: "did they choose a project that genuinely showcases their ability?",
    },
    {
      name: "Conciseness",
      description: "was the answer tight and structured rather than rambling?",
    },
    {
      name: "Delivery",
      description: "spoken fluency and confidence given the filler and pace stats",
    },
  ],
  created_at: null,
};
