# Category 16 — Scoring transparency UX

**Evidence:** [`../notes/16-scoring-transparency-ux.md`](../notes/16-scoring-transparency-ux.md)

## Bottom line

Keep **three** scorecard objects: how graded (score visible; rubric defs one tap away), why (rationale + transcript quote), what standard (citation chips **only** from retrieved IDs). Never ask the model for URLs; if retrieval is empty, say “Graded from rubric only.”

## Recommended CodeEcho actions

1. Progressive disclosure for dimension anchors (NN/g); don’t accordion-hide the score.
2. Persist `sources[]` from retrieve; render chips/`[n]` mapped to title/url/snippet.
3. No sources row when empty; never invent URLs (GhostCite hallucination rates when asked to cite closed-book).

## Sources

See note `16` (NN/g progressive disclosure, OpenAI/Anthropic/Gemini citation APIs, Perplexity cookbook, GhostCite arXiv).
