# Category 04 — RAG, corpora & grading transparency

**Parent report:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) §3.4  
**Evidence note:** [`../notes/04-rag-kb-transparency.md`](../notes/04-rag-kb-transparency.md)  
**Status:** researched · **Citation markers:** parent Sources table  
**User preference fit:** highest — **visible credibility**

## Bottom line

CodeEcho already has transcript “evidence”; retrieval titles/URLs are stripped before scoring [S18][S19][S20]. The free win is a **fourth channel**: sources with title + URL + snippet, plus static “how graded,” plus existing “why.” Prefer Markdown CC/MIT corpora and heading-aware chunks over more PDFs [S21][S22][S39][S40].

## Three UI objects (do not collapse)

1. **How graded** — static dimension text from `behavioral.py` / technical dims.
2. **Why this score** — rationale + transcript quote (already rendered).
3. **What standard** — retrieved snippet + title + canonical URL; if empty: “Graded from rubric only.”

Pattern analogue: OpenAI File Search `file_citation` — bind claims to retrieved objects only [S43].

## Corpora

| Source | License | Action |
|--------|---------|--------|
| system-design-primer | CC BY 4.0 | Ingest Markdown; attribute [S21][S36] |
| tech-interview-handbook | MIT | Ingest in-repo files only [S22] |
| coding-interview-university | CC BY-SA 4.0 | High ShareAlike risk — avoid or isolate [S37][S38] |
| Hello Interview | ToS NC, no copy/scrape | **Do not ingest** [S23] |
| interviewing.io | ToS + AI/competitor ban | **Do not ingest** [S24] |

## Chunking

Today: `pypdf` + 250/40 word windows, filename-only meta [S18].  
Upgrade: heading-aware Markdown, `Doc > H1 > H2` prefix, store `title`/`url`/`heading_path`; hybrid FTS+pgvector+RRF already matches Supabase free pattern [S39][S40][S41]. Prefer title-chain context over paid LLM-per-chunk [S42].

## Recommended CodeEcho actions

1. Persist retrieval metadata on scorecards; render Sources row.
2. Ingest SDP + TIH Markdown with attribution.
3. Expose “How graded” from existing dimension descriptions.
4. Never invent URLs in model output.

## Implementation hooks (in-repo today)

| Hook | Location | Gap |
|------|----------|-----|
| Scorecard UI | `frontend/src/components/ScorecardView.tsx` | Renders rationale / evidence quote / suggestion only — no sources row, no dimension definition on tap |
| Types | `frontend/src/lib/types.ts` (`Scorecard`, dimension `evidence`) | No `sources: {id,title,url,quote}[]` field yet |
| Retrieve | `backend/app/services/scoring.py` `_retrieve_reference` | Joins chunk **text** into the prompt; drops `meta` / URL before the judge |
| Ingest | `backend/scripts/ingest_kb.py` | PDF-only, 250/40 windows, filename meta — no Markdown / heading_path / url |
| Model answer | types already have model-answer fields | Keep separate from transcript `evidence` |

**Smallest free ship for credibility:** (1) add static “How this dimension is graded” from `behavioral.py` strings in the UI, (2) thread retrieval `title`+`url`+snippet onto the scorecard JSON, (3) render a “Sources used to grade” strip; empty → “Graded from rubric only.”
