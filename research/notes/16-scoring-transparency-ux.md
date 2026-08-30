# Note — Scoring transparency UX (how graded / why this score / what standard)

**Worker:** 16 · **Budget used:** 20/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** UI patterns that make AI/rubric scores recruiter-legible: rubric defs (progressive disclosure), rationale + evidence quote, citation/source chips. Interview or educational scorecards. Free. Out of scope: RAG licenses/corpora (04); multi-grader (03).

**Recommendation (evidence-weighted):** Keep three **separate** objects. (1) **How graded** = score + dimension name always visible; full anchors behind one tap (NN/g 2-level disclosure; Canvas rubric icon). Do not accordion-hide the number. (2) **Why this score** = existing rationale + transcript quote. (3) **What standard** = chips built only from **retrieved** `{id,title,url,snippet}` — never from model-emitted URLs. If retrieve is empty, say so; do not render a sources row.

## Findings

- **F1. Progressive disclosure is 2-level, not a dump and not a wizard.** Nielsen (2006-12-03): show the few frequent needs first; secondary only on request; presence on the first screen **signals importance**. Get the split right (frequent items stay out) and give the opener **strong information scent**. More than two levels “typically have low usability.” Staged/wizard disclosure is the wrong cousin here (users must walk every step). **S1** primary.

- **F2. Accordions fit rubric *definitions*, not the score.** Wang (2023-07-30): accordions *are* progressive disclosure; heading = gist, panel hidden. Benefits: less clutter, scan headings as a TOC. Costs: extra click, worse discoverability, a11y burden. **Do not hide crucial information** in the collapsed panel. Allow **multiple panels open** (auto-close blocks compare). If a reader needs most sections at once, skip accordions. Icons that work: caret or plus; whole heading clickable. **S2** primary. Fit: collapsed = “what STAR/Communication means”; never collapse the numeric score or one-line rationale.

- **F3. Educational scorecards already do icon-then-grid.** Canvas student Grades: score is in the row; a **Rubric icon** means “included a rubric for grading”; click → “view your score based on the rubric” → **Close Rubric**. Comments and scoring-details use the same icon-then-panel pattern. **S3** primary. Recruiter-legible analog: dim chip + score on the card; tap chip → anchors/BARS text (static, no retrieval).

- **F4. Citation UX is bind-then-render, not “ask the model for sources.”** Three first-party attachment models, same UI contract (claim span → retrieved object → chip):
  - **OpenAI File Search:** separate `file_search_call` item + `message` `output_text.annotations[]` of type `file_citation` (`index`, `file_id`, `filename`). Search is semantic+keyword. **`search_results` is null unless** `include: ["file_search_call.results"]`. Annotations are file-level, not quote-level, until you include results. **S4** primary.
  - **Anthropic Citations (docs + 2025-06-23 blog):** enable `citations.enabled` on documents **you** put in the request. Response = text blocks each with a `citations[]` (`cited_text` + location: char / page / content-block). `cited_text` is parsed out (not billed as output). Custom content = **your** chunks, no extra chunking — closest to labeled KB snippets. Blog: prompt-built citations were “inconsistent”; structured citations “minimize hallucinations.” Endex quote [marketing]: “source hallucinations… from 10% to 0%.” **S5** primary, **S6** primary [marketing] on the %.
  - **Gemini / Firebase Grounding:** `groundingChunks` (`uri`,`title`) + `groundingSupports` (text `startIndex`/`endIndex` → chunk indices) for **inline** source links. Tool present ≠ used: if the model does not search, **`groundingMetadata` is absent and the response is not a “grounded result.”** **S7** primary. `ai.google.dev` mirrors 50-redirect failed (Needs-browser); Firebase is the read Google page.

- **F5. Source chips: numbered inline + a strip built from retrieve metadata.** Perplexity Agent API cookbook (first-party): model inserts `[1]`/`[2]`; client maps `id` → `{title, url, snippet, date}`; “richer than a flat URL list — use it to build **source cards**, sidebars, or detailed reference sections.” Stream search_results **then** text; show a live citation count, full list when the stream ends. **S8** primary. Scorecard fit: `[n]` on rationale/suggestion only; one “Sources used to grade” row (favicon optional; title + domain enough). Do not put chips on the transcript **evidence** quote — that is channel 2, not 3.

- **F6. Anti-pattern A — invent sources.** Perplexity docs, exact: “Never ask the model to generate source URLs… Model-generated URLs can be hallucinated.” Use `search_results` only. **S8** primary. GhostCite (Xu et al., arXiv 2602.06718 v2 2026-05-14): when 13 LLMs are *asked to generate* citations, **all** hallucinate; rates **14.23%–94.93%**. Academic closed-book task, not RAG UI — still the reason chips must be minted from retrieve IDs. **S9** primary. Anthropic’s pitch is the same failure: prompt-built citations were inconsistent; structured citations exist to stop that. **S5, S6**.

- **F7. Anti-pattern B — hide empty retrieval / fake grounded chrome.** Firebase: no `groundingMetadata` ⇒ **not** a grounded result — do not paint source chips. **S7**. OpenAI: default `search_results: null` — filename annotations without included results are not excerpts. **S4**. Perplexity: if you keep only the first `search_results` batch, most `[N]` won’t resolve and “citations will look hallucinated.” **S8**. Honest empty state (derived): “Graded from rubric only — no KB match.” Never a sources row of invented or leftover IDs.

- **F8. Checkable CodeEcho mapping (derived).** ScorecardView already has rationale / evidence / suggestion; no sources row; evidence = transcript. Ship: (a) dim name + score + one-line rationale **always on**; (b) `?` or tap → static rubric sentence/anchors (F1–F3); (c) persist `sources: [{id,title,url,quote}]` from retrieve, render chips only for IDs that appear in that list (F4–F5); (d) empty retrieve → F7 copy, no strip; (e) never prompt the scorer to emit URLs (F6).

## Conflicts and uncertainty

- **OpenAI `index`:** official example is a character insert point on `output_text`; community threads argue older schemas used file-list index. Use current Responses `file_citation.index` as insert offset; do not treat it as a quote locator. Quote locator = included `file_search_call.results` or your own chunk ids.
- **Anthropic Citations vs RAG:** fetched docs cite **in-request** documents. A “search results as content blocks” page is linked but unread — do not claim the Citations API is a retriever.
- **Gemini Search Suggestions HTML** is a ToS display requirement for *Google Search grounding*. CodeEcho KB chips are not that product; do not copy the required search-suggestion widget.
- **GhostCite %** is generate-citations-from-memory, not “RAG still invents URLs.” Pair with **S8** for the UI rule.
- **Endex 10%→0% (S6)** is a named-customer quote on a vendor blog [marketing] [cherry-picked].
- **ZipTie / SEO “Perplexity pipeline” teardowns unread** — not used. Official cookbook only.
- **Canvas Enhanced Rubrics** (horizontal/vertical views, criterion description) seen only on university mirrors; not fetched as Instructure first-party. Student Grades icon pattern (**S3**) is the cited LMS interaction.
- **No first-party recruiter study** of scorecard chip layout. Transfer is analogical: NN/g + LMS + API citation contracts.
- Worker 04 owns corpora/licenses; this note does not re-litigate ingest.

## Quotes

- S1: "Initially, show users only a few of the most important options."
- S1: "the very fact that something appears on the initial display tells users that it's important"
- S2: "Avoid hiding any crucial information within the collapsed panels."
- S3: "An assignment may also include a Rubric icon, which means the assignment included a rubric"
- S4: "the file search call will not return search results by default"
- S5: "each text block can contain a claim that Claude is making and a list of citations"
- S6: "often resulting in inconsistent performance"
- S6: "reduced source hallucinations and formatting issues from 10% to 0%"
- S7: "the response won't contain a groundingMetadata object and thus it's not a \"grounded result\""
- S8: "Never ask the model to generate source URLs."
- S8: "citations will look hallucinated"
- S9: "all models hallucinate citations at rate from 14.23% to 94.93%"

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/progressive-disclosure/ | Progressive Disclosure — Nielsen | 2006-12-03 | primary | NN/g; 2-level; scent; [stale] examples |
| S2 | https://www.nngroup.com/articles/accordions-on-desktop/ | Accordions on Desktop — Wang | 2023-07-30 | primary | Don't hide crucial; multi-open |
| S3 | https://community.instructure.com/en/kb/articles/661305-how-do-i-view-my-grades-in-a-current-course | How do I view my grades… — Instructure | unknown | primary | Rubric icon → panel → close |
| S4 | https://developers.openai.com/api/docs/guides/tools-file-search | File search — OpenAI | unknown | primary | file_citation; results opt-in |
| S5 | https://platform.claude.com/docs/en/build-with-claude/citations | Citations — Claude docs | unknown | primary | cited_text + locations |
| S6 | https://claude.com/blog/introducing-citations-api | Introducing Citations — Anthropic | 2025-06-23 | primary | Product; Endex quote [marketing] |
| S7 | https://firebase.google.com/docs/ai-logic/grounding-google-search | Grounding with Google Search — Firebase | unknown | primary | chunks/supports; empty ≠ grounded |
| S8 | https://docs.perplexity.ai/docs/cookbook/articles/streaming-citations/README | Streaming Citation Parsing — Perplexity | unknown | primary | [n]↔id; never model URLs |
| S9 | https://arxiv.org/abs/2602.06718 | GhostCite — Xu et al. | 2026-02-06 / v2 2026-05-14 | primary | Abstract only; generate-cite task |

## Needs-browser

- https://ai.google.dev/gemini-api/docs/interactions/google-search — fetch.py exit 4 (curl 50 redirects). Same for `…/generate-content/google-search`. Used **S7** Firebase instead (same `groundingMetadata` contract).
- Instructure “Enhanced Rubrics / SpeedGrader” instructor guides — not fetched; university mirrors only in search. Lead: **S3** covers the student disclosure pattern.

## Searched

- OpenAI file citation annotations
- NN/g progressive disclosure
- Canvas SpeedGrader rubric UI
- Instructure Canvas how use rubric SpeedGrader
- Gemini grounding citations API
- Anthropic citations grounded answers
- Canvas how view rubric student
- citation hallucination LLM paper
- Perplexity how citations work
