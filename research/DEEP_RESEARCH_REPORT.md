# CodeEcho free-tier next steps — Deep Research Report

**Date:** 2026-08-30 · **Classification:** breadth-first
· **Workers:** 5 (+0 follow-up) · **Sources:** 45+ (primary-heavy across notes)
· **User prefs:** no binding deadline; **prefer visible credibility** over scoring depth

## 1. Bottom line

Under a free stack (Render sleep, Vercel Hobby, Supabase free, shared Stanford ~$3/day LLM **[unconfirmed publicly]** [S13]), the highest-ROI next steps are **make grading legible**—static “how graded,” transcript evidence you already collect, and **retrieval sources with title + URL**—then **honest wake/429 UX**, then a **zero-LLM substance-span layer**, then **Markdown CC/MIT corpora with heading-aware chunks**. Do **not** expand rubrics toward nine dimensions: first-party and platform scorecards use **3–4** competencies per interview [S1][S2], and joint multi-rubric LLM scoring shows **interference** (high-N setups are the stress case) [S9][S10]. Do **not** default to multi-grader ensembles: a strong single structured scorecard already approaches human agreement [S11], while debate (~4×) and per-trait sequential stacks (~8×) multiply calls [S12][S34].

## 2. Key findings

| # | Finding | Confidence | Sources |
|---|---------|-----------|---------|
| 1 | Credible SWE scorecards score **3–4** competencies per interview, not ~9 sections per answer; CodeEcho’s STAR path already lists ~8 dimensions in-repo (product inventory) | high for industry; high for local inventory | [S1][S2]; local `behavioral.py` |
| 2 | Joint multi-rubric LLM scoring shows **halo/interference**; isolation helps but multiplies calls; SARA reports only ~⅓ fully consistent across rubric-set changes | medium — SARA is new single-lab arXiv | [S9][S10] |
| 3 | GPT-4 single-answer judging already **85%** vs humans (human–human **81%**); ChatEval debate +2.5 pp on GPT-4 at ~4× calls | high | [S11][S12] |
| 4 | “No substance” is best as a **free heuristic span layer** (weasel/detail density + question overlap), folded into existing Specificity/Communication—not a 9th dim or second LLM | high for cost; medium for interview transfer | [S14][S15][S16][S17] |
| 5 | CodeEcho “evidence” is a **transcript quote**; retrieval `meta`/URLs are stripped before scoring—credibility gap is UX + metadata, not missing LLM axes | high (repo) | [S18][S19][S20] |
| 6 | Safe free corpora: System Design Primer (**CC BY 4.0**), Tech Interview Handbook (**MIT**); do **not** ingest Hello Interview or interviewing.io (ToS) | high | [S21][S22][S23][S24] |
| 7 | **Cost** order of idea classes: transparency + honest 429/cold-start ≈ $0 ≫ one-prompt rubric polish ≫ Markdown RAG ingest ≫ second grader (~2×). Credibility ranking elevates RAG/citations above dim polish (see §3.5 table) | high for infra docs; $ figures [unconfirmed] campus | [S25][S26][S27][S13] |
| 8 | From competitor marketing pages, a free **SWE rubric + delivery + voice** gap appears open; Warmup never graded answers and the official URL now points to tips + Gemini Live; Yoodli blogs are delivery-first | medium | [S14][S28][S29][S30][S31][S47] |

## 3. Detailed breakdown

### 3.1 Expanding to ~9 rubric sections — **do not**

Public hiring scorecards stay small. interviewing.io uses Code / Solve / Communicate (1–4) plus hire/no [S1]. Google re:Work lists three hiring-attribute categories with BARS-style anchors [S2]. Hello Interview’s published system-design themes and Meta E5 coding guide (vendor reconstructions, not first-party Meta docs) are both **four** axes including Communication [S4][S8]. Amazon’s sixteen Leadership Principles are culture/loop coverage, not a per-story nine-box scorecard [S3]. MIT’s STAR guide allocates **time** (Action 60%), not eight scored letters—coaching is deepen Action, not add sections [S7].

LLM-as-judge evidence pushes the same way. G-Eval uses four SummEval aspects and rates **one metric per prompt** [S5]. ComplexEval documents criteria entanglement (halo) and an attention ceiling under multi-dimensional complexity [S9]. SARA finds joint multi-rubric scoring systematically inconsistent (e.g. Qwen3-32B isolation-vs-joint exact-match **36%** on HealthBench; samples avg **11.5** rubrics, capped at 10 in their eval) [S10]. CodeEcho’s STAR path already lists Situation…Delivery (~8) in `behavioral.py`; moving to 9 increases joint-prompt tokens and interference surface without an industry precedent for nine per-answer sections.

**Implication (credibility-first):** if dimensions feel thin, **publish clearer anchors and show them in UI**, deepen Action/Specificity guidance, or optionally **collapse** Conciseness into Delivery—do not add two more boxes for a round number.

### 3.2 Low-substance / empty communication — **heuristic layer, not a new grader**

Google Interview Warmup explicitly did **not** grade answers; it surfaced patterns (job terms, frequent words, talking-point time) [S14]. Yoodli’s first-party blogs specify fillers, pace, talk time—not answer depth; treat homepage “content” claims as marketing until a metric page is read [S31]. Final Round AI’s “missing metric / thin action” language is vendor copy implying model-answer comparison [S32].

Named NLP constructs that *are* free: Wikipedia weasels / CoNLL-2010 hedges [S16]; VAGO-style detail/vagueness = named-entities+numbers over vague tokens [S15]. Hedge cues alone are **not** emptiness (a hedged but metric-rich claim can be high-substance) [S16][S17]. Embedding similarity is a weak relevance proxy (BERTScore ρ **0.312** vs G-Eval-4 **0.547** on SummEval Relevance) [S5].

**Implication:** implement span flags (weasel lexicons, number/NE density, question-term overlap), align to Whisper timestamps, optionally inject flagged spans into the **existing** Specificity/Communication prompt as evidence. Skip a second LLM pass and skip a ninth dimension.

### 3.3 Different types of graders — **keep one Pro scorecard**

A single structured multi-aspect scorecard (G-Eval / LLM-Eval shape) is the documented analogue of today’s CodeEcho call [S5][S33]. MT-Bench: GPT-4 single-answer agreement with humans **85%** vs human–human **81%** [S11]. ChatEval multi-agent debate adds **+2.5 pp** on GPT-4 at default **2 agents × 2 turns** (~4×) [S12]. Sequential per-trait essay scorers (MTS) help most when the holistic prompt is weak, at **8 calls** for 4 traits × 2 turns [S34]. Specialized open judges (Prometheus 2) need ~**16 GB VRAM**—not Render free 512 MB [S35].

Cost sketch using the project’s ~$0.02/attempt figure **[unconfirmed publicly]** and linear call scaling **[speculation]**: 1× ≈ 150 attempts/$3 day; ChatEval 4× ≈ 37; MTS 8× ≈ 18—before Whisper and question-gen share the campus ceiling [S13][S27].

**Viable extras:** embed a model/reference answer **in the same call**; optionally a **gated** second Pro pass for technical/math (MT-Bench reference-guided math failure **70% → 15%**) [S11]. Split content vs delivery as **two JSON sections** in one call. A Flash-delivery + Pro-substance split is an unpriced product pattern **[speculation]**—not measured in interview papers [note 03].

### 3.4 Better documents, chunking, and “links for how/why graded” — **priority for credibility**

**Corpora.** Prefer Markdown from OSI/CC repos over PDF dumps. Safe: `donnemartin/system-design-primer` CC BY 4.0 (credit + license link + mark changes) [S21][S36]; `yangshun/tech-interview-handbook` MIT (in-repo files only) [S22]. Avoid or carefully isolate `coding-interview-university` CC BY-SA 4.0 ShareAlike risk on adaptations [S37][S38]. **Do not ingest** Hello Interview (personal NC; no copy/download/scrape) [S23] or interviewing.io (explicit ban on using materials to develop/train AI or competing products) [S24]. STAR is a method, not an open corpus—write original rubric text; link public explainers.

**Chunking.** CodeEcho today: `pypdf` + 250/40 word windows, `meta.source` = filename only [S18]. Free upgrade: heading-aware Markdown chunks, prepend `Doc > H1 > H2`, store `title`, `url`, `heading_path` on rows so hybrid search can return them [S39][S40][S41]. Use title-chain prefixes, not paid LLM-per-chunk contextualization [S42]. Hybrid FTS + pgvector + RRF already matches Supabase’s free pattern [S39].

**Transparency UX (maps to user preference).** Keep three separate objects [S19][S20][S43]:

1. **How graded** — static dimension definitions from `behavioral.py` / technical dims (tap/expand).
2. **Why this score** — existing rationale + transcript evidence quote (already rendered; transcript highlighting exists).
3. **What standard** — retrieved snippet + title + canonical URL (new); if retrieval empty, say “Graded from rubric only.”

OpenAI File Search’s `file_citation` pattern (bind claims to retrieved objects, render markers) is the closest primary product analogue [S43]. Do not invent URLs in the model output—only show ids that were retrieved.

### 3.5 Free-tier economics and ranking

Render Free sleeps after **15 minutes** idle; official spin-up is “about one minute”; **750** instance-hours/month [S25]. Vercel Hobby can pause the frontend at **100%** included usage [S26]. Supabase Free: **500 MB** DB, **1 GB** storage, pause after a week idle [S44]. Gemini Agent Platform list prices show Flash ~**2.7–3.2×** cheaper than Pro on published SKUs—**not** an order of magnitude, and **not** the Stanford campus SKU [S27].

Portfolio guidance stresses a live demo someone can poke/break in about thirty seconds [S45], plus visible evals/citations/cost story on a short GitHub scan [S46]—not invisible architecture. From competitor marketing pages, a free SWE-specific rubric + delivery + voice gap appears open vs Yoodli (delivery), Hello Interview (paid curriculum), Final Round (paid stealth copilot); the official Warmup URL now serves tips + Gemini Live [S28][S29][S30][S47].

**Ranked next steps (credibility-first, free):**

| Rank | Work | Why | Cost |
|------|------|-----|------|
| 1 | **Grading transparency UI** (how / why / sources+links) | Directly matches user preference; uses signals already computed; recruiter-legible | ~$0 LLM |
| 2 | **Honest cold-start + Stanford 429 messaging**; no silent mock questions | Demo reliability; free | ~$0 |
| 3 | **Persist retrieval metadata + show citations**; Markdown ingest (SDP, TIH) + heading chunks | Makes RAG *visible*; license-safe | ingest/storage only |
| 4 | **Heuristic low-substance spans** + Whisper highlight | Improves Communication story without 2× LLM | CPU only |
| 5 | **Rubric polish** (clearer anchors; optional collapse; deepen Action/Specificity text)—**not** +2 dims | Aligns with 3–4 competency research | tiny prompt delta |
| 6 | Optional **in-prompt model answer** / gated technical reference pass | Quality where math/tech fails | +0–1× gated |
| — | **Default multi-grader / debate / Prometheus host** | Low visible gain, high $ and latency | ~4–8× / VRAM [S12][S34][S35] |
| — | **Expand to 9 dimensions** | Opposite of industry + interference evidence | more tokens, less trust |

Out of scope for this research pass (mentioned in prior product notes only): no-mic frozen demo path—not evaluated by workers 01–05.

**Category split (2026-08-30):** see [`INDEX.md`](./INDEX.md) and [`categories/`](./categories/). This file remains the canonical synthesis + Sources table for wave A.

## 9. Addendum — Wave B (recruiter shell)

**Date:** 2026-08-30 · **Audience:** A (recruiter/portfolio) · **Categories:** UI, reliability, mobile/a11y, SEO, auth  
**Details:** [`categories/00b-wave-b-roadmap.md`](./categories/00b-wave-b-roadmap.md) · notes `06`–`10`

For a resume-link click, a **synthesis** ranking of free work is: **(1)** honest wake/429/mock/STT states, **(2)** guest `/progress` without sign-in wall, **(3)** hero clarity (~10s role/what-this-is; craft later), **(4)** mic-on-tap + 44px targets + mobile scorecard a11y, **(5)** LICENSE/topics/README pitch + canonical/sitemap. Do not drop wave A’s grading-transparency #1.

Wave B claims are evidenced in `research/notes/06–10.md`. Citation audit (wave B): 22 supported / 6 weak / 0 unsupported / 3 miscited / 3 drift — miscited/drift fixed in category files.

## 10. Addendum — Waves C–E (remaining areas)

**Date:** 2026-08-30 · See [`categories/00c-waves-cde-roadmap.md`](./categories/00c-waves-cde-roadmap.md) and `categories/11`–`22`.

Remaining-area research complete: portfolio principles, no-mic homepage, cold-start, competitive landscape, voice recorder UX, scoring-transparency UX, eval harness, privacy/audio, cost metering UX, question bank, ESL delivery bias, guest/audio trust. Each has its own category `.md` and note. Citation audit (C–E): 85 supported / 6 weak / 0 unsupported / 0 miscited / 4 drift — hedges applied.

## 4. Conflicts and open questions

| Question | Position A | Position B | Better supported |
|----------|-----------|-----------|------------------|
| Expand dims for “richer” feedback? | More axes = finer coaching | 3–4 industry + joint-scoring interference (high-N stress) | B — primary hiring docs + LLM papers [S1][S2][S9][S10] |
| Multi-grader quality? | MTS/ChatEval gains on weak judges | Strong single judge ≈ human; GPT-4 debate +2.5 pp at 4× | Single scorecard for free tier [S11][S12][S34] |
| Yoodli “content”? | Homepage claims content | Blogs only define delivery metrics | Blogs [S31] over homepage marketing |
| Verbosity bias magnitude? | 2023 MT-Bench verbosity attacks | 2026 papers: style ≫ verbosity/position | Unresolved for interviews—don’t build on 2023 magnitudes alone [S11][S48][S49] |
| Interview Warmup sunset? | Official Grow page dated 2025-12-11 | Third-party “April 2026” | Prefer official page [S47]; tool itself is gone |

Unresolved:
- Exact CodeEcho $/attempt and Stanford reset window (project-internal; not public).
- Whether CC BY-SA CIU quotes in-app count as ShareAlike “adaptation.”
- No primary HireVue-style multi-grader method writeup found.
- Whether a local NER stack fits Render free 512 MB (not measured here); start with lexicon-only heuristics.

## 5. Timeline / data matrix

Deleted — not a temporal topic.

## 6. Implications

For CodeEcho with **visible credibility** preferred and **no deadline pressure**:

1. Ship the **three-channel scorecard** (how graded / why / sources with links) before any rubric expansion.
2. Treat RAG work as **citation infrastructure** (Markdown + metadata), not “more anonymous chunks.”
3. Improve Communication via **visible weak spans**, not another score row.
4. Keep **one** Gemini Pro structured scorecard; spend rare second calls only when technical reference grading fails a gate.
5. Refuse the round-number goal of nine sections; if anything, move toward fewer, better-anchored competencies that you can explain in the UI.

## 7. Sources

| id | url | title | published | tier | used for |
|----|-----|-------|-----------|------|----------|
| S1 | https://interviewing.io/blog/does-communication-matter-in-technical-interviewing-we-looked-at-100k-interviews-to-find-out | Communication vs Code/Solve (100K interviews) | unknown | primary | §3.1 |
| S2 | https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices | Google re:Work structured interviewing | 2026-03 | primary | §3.1 |
| S3 | https://www.aboutamazon.com/about-us/leadership-principles | Amazon Leadership Principles | unknown | primary | §3.1 |
| S4 | https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction | Hello Interview SD intro | unknown | secondary | §3.1 |
| S5 | https://ar5iv.labs.arxiv.org/html/2303.16634 | G-Eval (Liu et al.) | 2023 | primary | §3.1–3.3 |
| S7 | https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/ | MIT CAPD STAR | 2022-06-13 | primary | §3.1 |
| S8 | https://www.hellointerview.com/guides/meta/e5 | Meta E5 guide (Hello Interview) | unknown | secondary | §3.1 |
| S9 | https://arxiv.org/html/2509.03419 | ComplexEval / Curse of Knowledge | 2025 | primary | §3.1 |
| S10 | https://arxiv.org/html/2608.14684 | SARA rubric interference | 2026 | primary | §3.1 |
| S11 | https://arxiv.org/html/2306.05685v4 | MT-Bench / LLM-as-judge | 2023 | primary | §3.3 |
| S12 | https://arxiv.org/pdf/2308.07201 | ChatEval | 2023 | primary | §3.3 |
| S13 | note 03 cost table / project brief | ~$0.02/attempt, $3/day | — | secondary | §3.3 [unconfirmed $] |
| S14 | https://blog.google/company-news/outreach-and-initiatives/grow-with-google/interview-warmup/ | Interview Warmup launch | 2022-06-02 | primary | §3.2 |
| S15 | https://arxiv.org/html/2309.06132 | VAGO vagueness | 2023 | primary | §3.2 |
| S16 | https://aclanthology.org/W10-3001.pdf | CoNLL-2010 hedges/weasels | 2010 | primary | §3.2 |
| S17 | https://arxiv.org/pdf/2405.13319 | Hedge detection | 2024 | secondary | §3.2 |
| S18 | `backend/scripts/ingest_kb.py` | CodeEcho PDF ingest | local | primary | §3.4 |
| S19 | `backend/app/services/scoring.py` | Scoring prompts / retrieve | local | primary | §3.4 |
| S20 | `frontend/src/components/ScorecardView.tsx` | Scorecard UI | local | primary | §3.4 |
| S21 | https://raw.githubusercontent.com/donnemartin/system-design-primer/master/LICENSE.txt | SDP LICENSE | 2017 | primary | §3.4 |
| S22 | https://raw.githubusercontent.com/yangshun/tech-interview-handbook/master/LICENSE | TIH LICENSE | unknown | primary | §3.4 |
| S23 | https://www.hellointerview.com/terms | Hello Interview ToS | 2025-12-01 | primary | §3.4 |
| S24 | https://interviewing.io/terms | interviewing.io ToS | 2018-11-02 | primary | §3.4 |
| S25 | https://render.com/docs/free | Render Free | fetched 2026-08-30 | primary | §3.5 |
| S26 | https://vercel.com/docs/plans | Vercel plans | 2026-08-11 | primary | §3.5 |
| S27 | https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing | Gemini Agent Platform pricing | fetched 2026-08-30 | primary | §3.5 Flash≈3× Pro list (not campus) |
| S28 | https://yoodli.ai/use-cases/interview-preparation | Yoodli interview prep | unknown | primary/[marketing] | §3.5 |
| S29 | https://www.hellointerview.com/ | Hello Interview | unknown | primary/[marketing] | §3.5 |
| S30 | https://www.finalroundai.com/ | Final Round AI | unknown | primary/[marketing] | §3.5 |
| S31 | https://yoodli.ai/blog/how-to-stop-using-filler-words | Yoodli filler blog | 2023-01-16 | secondary | §3.2 |
| S32 | https://www.finalroundai.com/blog/interview-copilot-debrief | FRAI debrief | unknown | low | §3.2 |
| S33 | https://arxiv.org/abs/2412.05579v2 | LLMs-as-Judges survey | 2024 | primary | §3.3 |
| S34 | https://aclanthology.org/2024.findings-emnlp.10/ | MTS essay scoring | 2024 | primary | §3.3 |
| S35 | https://github.com/prometheus-eval/prometheus-eval | Prometheus 2 README | 2024 | primary | §3.3 |
| S36 | https://creativecommons.org/licenses/by/4.0/ | CC BY 4.0 deed | unknown | primary | §3.4 |
| S37 | https://raw.githubusercontent.com/jwasham/coding-interview-university/main/LICENSE.txt | CIU LICENSE | unknown | primary | §3.4 |
| S38 | https://creativecommons.org/licenses/by-sa/4.0/ | CC BY-SA 4.0 deed | unknown | primary | §3.4 |
| S39 | https://supabase.com/docs/guides/ai/hybrid-search | Supabase hybrid search | 2026-08-28 | primary | §3.4 |
| S40 | https://samuelochoa.com/expertise/rag/chunking/structure-aware | Structure-aware chunking | 2026-04-18 | secondary | §3.4 |
| S41 | https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/ | LlamaIndex node parsers | unknown | primary | §3.4 |
| S42 | https://www.anthropic.com/engineering/contextual-retrieval | Contextual Retrieval | 2024-09-19 | primary/[vendor] | §3.4 |
| S43 | https://developers.openai.com/api/docs/guides/tools-file-search | OpenAI File Search | unknown | primary | §3.4 |
| S44 | https://supabase.com/pricing | Supabase pricing | fetched 2026-08-30 | primary | §3.5 |
| S45 | https://ai-tldr.dev/learn/building-ai-apps/ai-career-path/build-ai-portfolio/ | AI portfolio guide | 2026-06-11 | secondary | §3.5 |
| S46 | https://github.com/landedjobs/ai-engineer-portfolio-projects | Portfolio catalog | 2026-07 | secondary | §3.5 |
| S47 | https://grow.google/interview-warmup | Grow with Google interview page | 2025-12-11 | primary | §3.5 |
| S48 | https://arxiv.org/html/2606.19544v1 | Reliability without Validity | 2026-06 | primary | §4 |
| S49 | https://arxiv.org/html/2604.23178 | Judging the Judges | 2026-04 | primary | §4 |

## 8. Method and audit

- Plan: `research/PLAN.md`
- Worker notes: `research/notes/` (5 files, retained) — [01](notes/01-rubric-dimensions.md), [02](notes/02-substance-depth.md), [03](notes/03-grader-designs.md), [04](notes/04-rag-kb-transparency.md), [05](notes/05-free-tier-roi.md)
- Wave 2: skipped (convergent findings; Needs-browser leftovers non-decisive)
- Citation audit (pass 1): 48 supported / 6 weak / 2 unsupported / 3 miscited / 5 drift — unsupported deleted; miscited/weak/drift fixed in-place
- Citation audit (pass 2): 24 supported / 3 weak / 0 unsupported / 1 miscited / 0 drift on re-check — remaining miscited (S7 on Finding 1) fixed; residual weaks polished
- Known gaps: campus Gemini SKUs unread; pypdf caveats 404; Anthropic RAG %s are vendor domains not interview transcripts; SARA unreplicated; no-mic path not researched this pass
