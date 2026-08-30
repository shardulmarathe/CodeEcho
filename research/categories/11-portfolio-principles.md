# Category 11 — Portfolio / good-project principles

**Evidence:** [`../notes/11-portfolio-principles.md`](../notes/11-portfolio-principles.md)  
**Audience:** recruiter / portfolio

## Bottom line

Strong free-tier AI demos are often judged with **~30s live poke** and **~90s GitHub scan** heuristics (secondary portfolio guides): working URL, visible evals, citations, cost/latency, README-as-spec—not a silent Whisper+LLM wrapper.

## Checkable principles → CodeEcho

| Principle | Pass if… | CodeEcho gap |
|-----------|----------|--------------|
| Live poke works | Click without clone; survive a break attempt | Wake/429/mock honesty (cat 07) |
| Evals visible | N/M + shown failures in README or UI | No golden-set table/CI surfaced |
| Citations visible | Sources on scorecards | Cat 04 (not shipped) |
| Cost/latency named | $/attempt or budget + cold-start called out | Metering exists; not recruiter-visible |
| README funnel | Pitch, live link, GIF/screenshot, X-over-Y, limits | README partially stale |
| Not a wrapper | Scoped workflow + measurement + ops | Dual-axis + RAG already help—make visible |

## Recommended actions

1. Ship honest degrade states before new features.
2. Publish a small golden-set / stress-harness summary in README.
3. Citation UI + cost line on scorecard or `/account`.
4. Rehearse Vercel pause + Render sleep before sharing resume links.

## Sources

See note `11` (ai-tldr, landedjobs, GitHub docs, Chip Huyen, Hamel evals, Render/Vercel).
