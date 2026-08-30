# 04 — RAG corpora, chunking, citation UX (interview-prep)

**Worker:** research-worker · **Date:** 2026-08-30 · **Scope:** public corpora + licenses, chunking/hybrid retrieval, "why this score" UX. Free stack only (Supabase/pgvector). Three tracks kept separate: (A) better source docs, (B) chunking/retrieval, (C) citation UX.

## Findings

### A. Corpora and licenses (ingest vs link-only)

- **Ingest Markdown from OSI/CC repos, not PDF dumps of the same text.** Structure-aware chunkers treat Markdown headings/code/tables as first-class; PDFs have no guaranteed structure and depend on parser quality [S6]. CodeEcho today only glob-ingests `*.pdf` via `pypdf.PdfReader.extract_text()`, 250-word windows, 40-word overlap, `meta={source: filename, bucket, chunk}` — no URL, no heading path [S13].
- **Safe-to-ingest (license from repo LICENSE, not README prose):**
  - `donnemartin/system-design-primer`: CC BY 4.0, © 2017 Donne Martin; license is from him, not Facebook [S2]. CC BY requires credit, license link, and mark of changes; commercial reuse allowed [S3]. Prefer raw `.md` / `solutions/` over a printed PDF.
  - `yangshun/tech-interview-handbook`: MIT, © 2017–Present Yangshun Tay; retain copyright notice in copies [S7]. [unconfirmed] whether every linked third-party article in that repo is also MIT — ingest only files in-repo.
  - `jwasham/coding-interview-university`: CC BY-SA 4.0 [S8]. ShareAlike: adapted material (chunked/rewritten coaching text derived from it) must be distributed under the same license [S9]. Attribution + license link required. High ShareAlike risk if CodeEcho's KB or generated "model answers" are treated as adaptations.
- **Do not ingest (ToS, not open license):**
  - Hello Interview (Optick Labs): last revised 2025-12-01. License is personal, noncommercial, revocable. "no part of the website may be copied, reproduced, published, downloaded" unless expressly stated; automated scrape/mine forbidden except public-search-engine spiders per robots.txt [S5].
  - interviewing.io: effective 2018-11-02. Personal, non-commercial only. Ban on download/copy/reproduce of "Interviewing Materials" without written consent; ban on robots/scrape; **explicit ban** on using the Service or materials to develop/train/operate ML/AI models or competing products [S10].
- **STAR / behavioral guides:** no primary open STAR *corpus* found this pass. STAR is a method, not a license. University career PDFs are typically all-rights-reserved — **link** to a public explainer; write original rubric text in-house. Do not scrape interview-coach blogs.
- **Link-only (cite, don't chunk):** company official interview pages, Amazon LPs, paid books (CTCI, Grokking), Hello Interview free HTML, interviewing.io articles. Recruiter-legible "how graded" can point at *your* rubric definitions + CC/MIT sources, not scraped premium breakdowns.

### B. Chunking and hybrid retrieval (short spoken answers)

- **Hybrid FTS + pgvector + RRF is the official free-Postgres pattern and matches CodeEcho.** Supabase: separate `tsvector` (GIN) and `embedding` (HNSW) CTEs, `FULL OUTER JOIN`, score `1/(rrf_k+rank)` with default `rrf_k=50`, optional `full_text_weight` / `semantic_weight`; function `returns setof documents` so extra columns (title, url, heading) come back if stored on the row [S1]. Keyword path uses `websearch_to_tsquery`. Caps each branch at `least(match_count,30)*2`.
- **Why hybrid helps spoken-answer grading:** transcripts paraphrase ("I sharded the write path") while rubrics need exact tokens (STAR, CAP, p99, Big-O). Anthropic: embeddings miss exact IDs; BM25 catches them; combine with rank fusion; then rerank [S4]. CodeEcho already hybrid-RRF in `kb_store`; prod cross-encoder rerank is OFF per brief — Anthropic says rerank *stacks* on hybrid (their 49% → 67% failure drop) [S4][vendor eval][cherry-picked domains].
- **Chunk size:** Anthropic RAG primer: "usually no more than a few hundred tokens" [S4]. CodeEcho's 250 words ≈ that band. Problem is *boundary*, not size: word windows split mid-section and drop heading context [S13][S6].
- **Heading-aware + title-chain prefix is the free contextualization.** Parse Markdown AST; one chunk per section; split large sections on subheads/paragraphs; never split tables/code; never merge across H1; prepend `# Doc > H1 > H2` (or store as metadata also embedded) [S6]. LlamaIndex: child nodes inherit parent document `metadata` — the hook for `source_url` / title on every chunk [S12]. Anthropic "Contextual Retrieval" instead LLM-generates 50–100 token situating prefixes per chunk; they report 35% fewer top-20 misses (embeddings only) and 49% with contextual BM25; generic *document summaries* on chunks had "very limited gains" vs chunk-specific context [S4][vendor]. Cost they quote: $1.02 / million document tokens with prompt caching [S4][marketing]. **For free-tier CodeEcho: title-chain prefix, not Haiku-per-chunk.**
- **If the whole KB is tiny:** Anthropic says a corpus under ~200k tokens (~500 pages) can be stuffed in-prompt with caching and skip RAG [S4][speculation for current ~18 PDFs]. Still keep structured chunks if you want *citations*.
- **Query for spoken answers:** retrieve with question + bucket + (optional) transcript keywords (STAR verbs, tech nouns), not question text alone. Weight FTS up when the rubric is lexical (dimension names, "STAR", "latency"). [inference from S1+S4; not A/B tested here]
- **PDF types that chunk poorly:** scanned/image PDFs (no text layer → ingest skip already [S13]); slide decks and two-column papers (reading order wrong); table-heavy design docs (tables must stay atomic [S6]); "print to PDF" of HTML/Markdown (destroys headings you already had). **Better artifact = the `.md` file, not a better PDF.** pypdf extraction-improvements doc 404'd this pass (Needs-browser).

### C. "Why this score" UX (separate from better PDFs)

- **CodeEcho already has a 3-slot scorecard; it is not a citation UI.** Prompt requires per dimension: rationale, **evidence = quote from the transcript**, suggestion [S14]. `ScorecardView` renders those three; rubric is a label string only (`experience` → "STAR") [S15]. `_retrieve_reference` joins chunk **content only** — `ref`/`meta.source` discarded before the scorer [S14]. So "evidence" ≠ retrieval proof. Recruiter-legible work is a **fourth channel**, not replacing evidence quotes.
- **Credible product pattern (primary): bind claims to retrieved objects, then render markers.** OpenAI File Search returns `file_citation` annotations on `output_text` with `file_id` + `filename` (+ index); retrieval is "semantic and keyword search"; `file_search_call` is a separate output item from the message [S11]. Fit: store `source_url`, `title`, `heading_path`, `chunk_id` on each `kb_documents` row (Supabase already returns `documents.*` [S1]); after retrieve, pass **labeled** blocks (`[1] title — url — quote`) into the scorer; persist `sources: [{id, title, url, quote}]` on the scorecard; render `[1]` on rationale/suggestion only when that id was retrieved (do not let the model invent URLs).
- **Secondary UX (teardowns, not official Perplexity docs):** numbered inline markers + always-visible sources strip (favicon/domain/title/snippet); hover = excerpt [S16]. For CodeEcho, a compact "Sources used to grade" row under the overall summary is enough; per-dimension chips if a source was used for that dim.
- **Three user questions → three UI objects (do not collapse):**
  1. **How graded:** static rubric definition (the dimension sentence already in `behavioral`/`TECHNICAL_DIMENSIONS`) shown on tap — no retrieval needed, free, high recruiter-legibility.
  2. **Why this score:** existing rationale + transcript `evidence` quote [S14][S15].
  3. **What standard:** retrieved snippet + title + canonical URL (CC-BY attribution also satisfies [S3][S9]). Optional "model answer" is a *separate* field (`ModelAnswer` already exists in types) — do not stuff it into `evidence`.
- **Grounding honesty:** if retrieval is empty, show "Graded from rubric only — no KB match" rather than implied sources. OpenAI leaves `search_results` null unless included [S11]. Do not claim "grounded AI" without showing the chunk.

## Conflicts and uncertainty

- Anthropic 49%/67% figures are vendor-internal across their domains (code, fiction, ArXiv, science), metric = 1−recall@20, embeddings = Gemini in the headline chart [S4]. Not interview-transcript RAG. Treat as directional, not a CodeEcho SLA.
- Cormack RRF often uses k=60 in blogs; Supabase default `rrf_k=50` [S1]. Not a conflict of method, just a knob.
- MIT on TIH covers "software and associated documentation files" [S7]; third-party content linked from that handbook was not license-checked.
- CC BY-SA on CIU vs a closed-source product: whether showing a retrieved quote in-app is "Share" (OK with attribution) vs shipping an "Adapted" derived KB (ShareAlike on the adaptation) is a legal judgment, not resolved here.
- interviewing.io ToS AI-training clause is unusually broad [S10]; even *linking* their articles in a scorecard is probably fine; ingesting is not.
- Hello Interview has a free content surface; ToS still forbids copy/download of site content [S5]. "Free to read" ≠ "free to ingest."
- No official Perplexity citation spec read; UX notes are secondary teardowns [S16].
- Current on-disk `kb_sources` listing in this workspace showed one PDF + README; brief says ~18 PDFs — some may be gitignored. Not re-audited.
- pypdf official extraction caveats not confirmed (404).
- Out of scope (other workers): extra rubric dims, substance detection, multi-grader, portfolio ROI.

## Quotes

- SDP license: "Creative Commons Attribution 4.0 International License (CC BY 4.0)" [S2]
- Hello Interview: "no part of the website may be copied, reproduced, published, downloaded" [S5]
- interviewing.io: "developing, training, or operating any machine learning or artificial intelligence models" [S10]
- Anthropic: "usually no more than a few hundred tokens" [S4]
- Anthropic: "reduce the number of failed retrievals by 49% and, when combined with reranking, by 67%" [S4]
- CodeEcho prompt: "a short evidence quote pulled from the answer" [S14]
- OpenAI: "the response from the model, along with the file citations" [S11]

## Sources

id | url | title | published | tier | note
---|---|---|---|---|---
S1 | https://supabase.com/docs/guides/ai/hybrid-search | Hybrid search \| Supabase Docs | 2026-08-28 (page) | primary | Official RRF + tsvector + pgvector; returns `documents.*`
S2 | https://raw.githubusercontent.com/donnemartin/system-design-primer/master/LICENSE.txt | system-design-primer LICENSE.txt | 2017 (copyright) | primary | CC BY 4.0; personal, not Facebook
S3 | https://creativecommons.org/licenses/by/4.0/ | CC BY 4.0 Deed | unknown | primary | Share/adapt + attribution; deed ≠ legal code
S4 | https://www.anthropic.com/engineering/contextual-retrieval | Contextual Retrieval in AI Systems | 2024-09-19 | primary | Vendor eval; hybrid+context+rerank; [marketing] cost
S5 | https://www.hellointerview.com/terms | Hello Interview Terms of Use | 2025-12-01 | primary | Personal NC; no copy/download/scrape
S6 | https://samuelochoa.com/expertise/rag/chunking/structure-aware | Structure-aware chunking | 2026-04-18 | secondary | Personal eng blog; heading-path; PDF parser-dependent
S7 | https://raw.githubusercontent.com/yangshun/tech-interview-handbook/master/LICENSE | tech-interview-handbook LICENSE | unknown | primary | MIT, Yangshun Tay
S8 | https://raw.githubusercontent.com/jwasham/coding-interview-university/main/LICENSE.txt | coding-interview-university LICENSE.txt | unknown | primary | CC BY-SA 4.0 full text
S9 | https://creativecommons.org/licenses/by-sa/4.0/ | CC BY-SA 4.0 Deed | unknown | primary | Attribution + ShareAlike
S10 | https://interviewing.io/terms | Interviewing.io Terms of Use | 2018-11-02 | primary | NC; no scrape; AI/ML + competitor ban
S11 | https://developers.openai.com/api/docs/guides/tools-file-search | File search \| OpenAI API | unknown | primary | `file_citation` annotations; semantic+keyword
S12 | https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/ | Node Parser Usage Pattern | unknown | primary | Child nodes inherit document metadata
S13 | `backend/scripts/ingest_kb.py` | CodeEcho PDF ingest | local | primary | pypdf; 250/40 word chunks; filename meta only
S14 | `backend/app/services/scoring.py` | CodeEcho scoring prompts | local | primary | evidence=transcript quote; refs stripped
S15 | `frontend/src/components/ScorecardView.tsx` | ScorecardView | local | primary | rationale/evidence/suggestion; no sources
S16 | https://blakecrosley.com/guides/design/perplexity | Perplexity: AI-Native Search Design | unknown | secondary | Teardown; inline cites + sources panel

## Needs-browser

- https://pypdf.readthedocs.io/en/stable/user/extraction-improvements.html — fetch.py exit 4 (HTTP 404). Need live pypdf extract-text caveats.
- LlamaIndex `MarkdownNodeParser` module page not fetched (only parent node-parsers overview [S12]).

## Searched

- pgvector hybrid search citations
- RAG heading aware chunking
- system design primer license
- Anthropic contextual retrieval chunking
- Hello Interview terms license
- Perplexity citation sources UX
- OpenAI file search citations
