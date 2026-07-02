// Human-friendly labels for the LLM "why your fillers happen" tags.

export const TAG_LABELS: Record<string, string> = {
  idea_transition: "Idea transition",
  topic_mention: "Topic mention",
  hesitation: "Hesitation / word recall",
};

export const TAG_ORDER = ["idea_transition", "topic_mention", "hesitation"];

export function tagLabel(tag?: string | null): string {
  if (!tag) return "";
  return TAG_LABELS[tag] ?? tag.replace(/_/g, " ");
}
