# Ranked roadmap — credibility-first, free tier

**Parent:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) · **Date:** 2026-08-30  
**Prefs:** visible credibility > scoring depth · no binding deadline · $0 infra

## Bottom line

Ship **grading transparency** and **honest failure UX** before more dimensions, more graders, or bigger anonymous RAG.

## Do (ranked)

| Rank | Work | Category | Cost |
|------|------|----------|------|
| 1 | Three-channel scorecard: how graded / why / sources+links | [04-rag-transparency](./04-rag-transparency.md) | ~$0 LLM |
| 2 | Honest cold-start + Stanford 429 messaging; no silent mock questions | [05-free-tier-roi](./05-free-tier-roi.md) | ~$0 |
| 3 | Persist retrieval metadata; Markdown ingest (SDP, TIH) + heading chunks | [04-rag-transparency](./04-rag-transparency.md) | ingest/storage |
| 4 | Heuristic low-substance spans + Whisper highlight | [02-substance-communication](./02-substance-communication.md) | CPU only |
| 5 | Rubric polish (clearer anchors; optional collapse)—**not** +2 dims | [01-scoring-rubrics](./01-scoring-rubrics.md) | tiny prompt delta |
| 6 | Optional in-prompt model answer / gated technical reference pass | [03-grader-architecture](./03-grader-architecture.md) | +0–1× gated |

## Do not (default)

| Anti-goal | Why | Category |
|-----------|-----|----------|
| Expand to ~9 dimensions | Industry uses 3–4; joint LLM rubrics interfere | [01](./01-scoring-rubrics.md) |
| Default multi-grader / debate / Prometheus on Render | ~4–8× calls or ~16 GB VRAM | [03](./03-grader-architecture.md) |
| Ingest Hello Interview / interviewing.io | ToS forbid copy/scrape/AI training use | [04](./04-rag-transparency.md) |

## Implications checklist

1. Three-channel scorecard before rubric expansion.
2. RAG = citation infrastructure, not more anonymous chunks.
3. Communication via **visible** weak spans, not another score row.
4. Keep **one** Gemini Pro structured scorecard.
5. Prefer fewer, UI-explainable competencies over a round number of nine.

## Suggested first implementation slice (if Q4 = B)

Ordered for visible credibility + free tier; details in category files:

1. **Scorecard transparency** — How graded + Sources strip ([04](./04-rag-transparency.md) hooks)
2. **Honest wake / 429 / mock banners** ([05](./05-free-tier-roi.md) hooks)

Do not start this slice until expansion research is confirmed **or** the user explicitly says implement-from-current-roadmap.

## Out of scope (this research set)

No-mic frozen demo path — not evaluated by workers 01–05; may become a category after user direction.
