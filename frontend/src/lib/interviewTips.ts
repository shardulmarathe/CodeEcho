export type InterviewTipTheme = "structure" | "technical" | "delivery" | "mindset";

export interface InterviewTip {
  id: string;
  theme: InterviewTipTheme;
  title: string;
  body: string;
}

export const INTERVIEW_TIPS: InterviewTip[] = [
  {
    id: "star-specific-result",
    theme: "structure",
    title: "Make STAR land with evidence",
    body: "A strong behavioral answer ends with a concrete result: a number, a user impact, or a clear lesson learned.",
  },
  {
    id: "one-sentence-situation",
    theme: "structure",
    title: "Keep the setup short",
    body: "Spend one sentence on context, then move quickly into what you personally did and why it mattered.",
  },
  {
    id: "own-your-actions",
    theme: "structure",
    title: 'Use "I" for your contribution',
    body: 'Interviewers need to understand your role. Use "we" for team context and "I" for decisions, tradeoffs, and execution.',
  },
  {
    id: "close-the-loop",
    theme: "structure",
    title: "Close the loop",
    body: "After describing the action, say what changed because of it. Outcomes make your story feel complete.",
  },
  {
    id: "conflict-growth",
    theme: "structure",
    title: "Conflict answers need growth",
    body: "For conflict or failure questions, the strongest ending is what you changed in your process afterward.",
  },
  {
    id: "clarify-before-solving",
    theme: "technical",
    title: "Clarify before coding",
    body: "A few targeted questions about constraints and edge cases can make your solution sound much more senior.",
  },
  {
    id: "name-the-bruteforce",
    theme: "technical",
    title: "Start with the obvious path",
    body: "Briefly name the brute-force solution before optimizing. It shows the interviewer how you reasoned your way forward.",
  },
  {
    id: "tradeoff-language",
    theme: "technical",
    title: "Call out tradeoffs",
    body: "Great technical answers explain not just what works, but why that approach beats the alternatives for this problem.",
  },
  {
    id: "complexity-checkpoint",
    theme: "technical",
    title: "Say the complexity out loud",
    body: "Even if it feels obvious, stating time and space complexity helps the interviewer calibrate your solution quickly.",
  },
  {
    id: "edge-case-bucket",
    theme: "technical",
    title: "Group edge cases",
    body: "Name edge cases in buckets: empty input, duplicates, boundaries, scale, and invalid data. It sounds organized and complete.",
  },
  {
    id: "think-in-invariants",
    theme: "technical",
    title: "Use invariants",
    body: "When explaining algorithms, state the condition that always remains true. It makes correctness easier to follow.",
  },
  {
    id: "pause-before-answer",
    theme: "delivery",
    title: "A pause beats a filler",
    body: 'A half-second pause sounds more confident than filling the gap with "um," "like," or "you know."',
  },
  {
    id: "slow-first-sentence",
    theme: "delivery",
    title: "Slow the first sentence",
    body: "Your opening sentence sets the pace. Start a little slower than feels natural, then settle into rhythm.",
  },
  {
    id: "signpost-sections",
    theme: "delivery",
    title: "Signpost your answer",
    body: 'Phrases like "First," "The tradeoff is," and "The key result was" help listeners track your structure.',
  },
  {
    id: "breath-before-result",
    theme: "delivery",
    title: "Breathe before the result",
    body: "Pause right before the outcome of your story. It makes the payoff clearer and reduces rushed endings.",
  },
  {
    id: "avoid-upward-trail",
    theme: "delivery",
    title: "End with confidence",
    body: "Try not to let every sentence trail upward like a question. A firm ending makes your answer sound more decisive.",
  },
  {
    id: "repeat-question",
    theme: "mindset",
    title: "Restate the target",
    body: "Before answering a complex question, restate what you think they are asking. It buys thinking time and prevents misses.",
  },
  {
    id: "admit-uncertainty",
    theme: "mindset",
    title: "Uncertainty can sound senior",
    body: "If you are not sure, say your assumption and proceed. Interviewers reward clear reasoning more than pretending.",
  },
  {
    id: "ask-for-signal",
    theme: "mindset",
    title: "Use the interviewer",
    body: "If you are choosing between two paths, say the tradeoff and ask whether they want depth in one direction.",
  },
  {
    id: "answer-then-explain",
    theme: "mindset",
    title: "Lead with the answer",
    body: "For direct questions, give the short answer first, then explain. It keeps your response from feeling evasive.",
  },
  {
    id: "specific-over-polished",
    theme: "mindset",
    title: "Specific beats polished",
    body: "A real detail from your work is usually more convincing than a perfectly generic interview phrase.",
  },
  {
    id: "check-for-followup",
    theme: "mindset",
    title: "Invite a follow-up",
    body: 'After a dense answer, a simple "I can go deeper on the implementation if useful" shows control and openness.',
  },
  {
    id: "name-the-risk",
    theme: "technical",
    title: "Name the risk",
    body: "For system design or project answers, call out the main failure mode and how you would monitor or mitigate it.",
  },
  {
    id: "metric-memory",
    theme: "structure",
    title: "Keep two metrics ready",
    body: "Prepare a latency, cost, adoption, revenue, quality, or reliability metric from your work. Numbers make stories stick.",
  },
  {
    id: "finish-with-learning",
    theme: "structure",
    title: "End with what transferred",
    body: "A strong answer often closes with how that experience changed how you approach similar problems now.",
  },
];

export function pickRandomTip(excludeId?: string): InterviewTip {
  const candidates = INTERVIEW_TIPS.filter((tip) => tip.id !== excludeId);
  const pool = candidates.length ? candidates : INTERVIEW_TIPS;
  return pool[Math.floor(Math.random() * pool.length)];
}

export function rotateTip(currentId?: string): InterviewTip {
  return pickRandomTip(currentId);
}
