# CodeEcho — next steps

Written 2026-08-28. This is a standalone brief: a fresh session should be able to
pick up from here with no prior context. Read `ARCHITECTURE.md` alongside it for how
the system works; this document is only about what to do next and why.

---

## 0. RESOLVED — production was broken, root cause found

**Fixed 2026-08-29.** Recorded because the failure mode is the interesting part.

**Symptom.** Every LLM call on production failed, so `questions.py` silently served
offline mock-bank questions and scoring 503'd. `/api/health` reported
`gemini_configured: true` throughout, and `/api/budget` reported spend well under
cap. Nothing looked wrong.

**Root cause.** A stale, revoked `GEMINI_API_KEY` on Render. Every call returned
`401 Invalid proxy server token`.

**Why it took hours instead of minutes.** `generate_question()` caught every
exception and returned a mock question with no logging. A broken production was
byte-for-byte indistinguishable from working offline mode. Two wrong theories got
chased first — a budget-cap env var, then upstream pool exhaustion — before logging
was added and the actual 401 surfaced.

**A second trap found alongside it.** `~/.zshrc` exported `GEMINI_API_KEY`, and a
real env var takes precedence over a project `.env` in pydantic-settings. So
editing `backend/.env` appeared to do nothing locally: the stale shell export won
silently. Both are now synced to the working key, with a warning comment in
`.zshrc`.

**Verified working:** behavioral and technical question generation return fresh
LLM output, interview orchestration builds its plan, and recorded spend increments.

**The durable lessons, both now in section 6:**
- Never let a fallback be silent. A graceful degradation you cannot observe is
  indistinguishable from an outage, and it will cost hours.
- A shell export shadows a project `.env`. Check `os.environ` before trusting a
  config file you just edited.
- Do not change an env var whose semantics only exist in undeployed code.

---

## 0b. The budget cap does not measure what it thinks it measures

Found 2026-08-29 while stress-testing. The app's own ledger and Stanford's ledger
are different numbers, and only Stanford's can actually stop you.

```
CodeEcho  GET /api/budget   ->  {"cap_usd": 2.5, "spent_usd": 0.0}
Stanford  api.llm.stanford.edu -> 429 "Budget has been exceeded!
                                       Current cost: 3.0, Max budget: 3.0"
```

`spent_usd: 0.0` and simultaneously hard-capped upstream. Two causes, both real:

1. **Different reset windows.** `budget.py` resets at UTC midnight (`_today()`).
   Stanford's counter clearly does not — the UTC day had just rolled over to
   2026-08-29 and CodeEcho read zero while Stanford still read 3.0/3.0.
2. **The key is not exclusive to CodeEcho.** Anything else using it — `gemini-cli`,
   other projects, other experiments — spends the same $3.00 and CodeEcho never
   sees it.

**Consequence:** `API_BUDGET_CAP_USD` cannot protect the key. It is a local
estimate of a counter it does not own. Tightening it from $25 to $2.50 was
directionally right but does not achieve the goal, because the app can read $0.00
spent while the upstream is fully exhausted.

**What to do instead — this is a plan change, not a bug fix:**

- **Handle 429 gracefully and say so.** Right now `questions.py` catches the error
  and silently serves a mock-bank question; `scoring.py` surfaces
  `ScoringUnavailable` as a 503. A user cannot tell "the shared daily budget is
  used up, try tomorrow" from "the app is broken". For a recruiter demo that
  distinction is everything. **Treat upstream 429 as a first-class state with its
  own honest message.**
- **Trust upstream over the local estimate.** On a 429, record the day as exhausted
  locally so subsequent requests fail fast with the right message instead of
  hammering a capped key.
- **Do not remove the local cap.** It still bounds a runaway loop, which is what it
  is actually good for. Just stop treating it as the real limit.

**For the demo specifically (deadline risk):** if a recruiter clicks the link on a
day the key is already spent, they get mock questions and 503s on scoring. This is
now a top-tier risk to the two-week goal, and it is a strong argument for
workstream B2 (the no-microphone path with frozen real output) doing double duty —
**frozen sample output does not depend on the key at all.**

---

## 1. Goal and constraints

These were chosen deliberately. Do not silently relax them.

| | |
|---|---|
| **Purpose** | Portfolio / demo piece. |
| **Reviewer** | **A recruiter, not an engineer.** They will not read the code. They will not run it locally. They will click a link, look for 30–60 seconds, and form a judgement. |
| **Deadline** | **~2026-09-11 (two weeks from 2026-08-28).** Scope is cut to fit; see section 3a. |
| **Infra budget** | **$0.** Render free tier, Supabase free tier, Vercel Hobby stay as they are. |
| **LLM** | Stanford proxy key, **hard $3/day ceiling imposed by Stanford**, shared across all users. |
| **Question strategy** | Hybrid: a curated seed bank retrieved first, generation as fallback. |
| **What "polished" means** | All four of: feedback credibility, reliability, visual craft, speed. |

### What the constraints imply

The free tier is not a detail, it is the design. Render sleeps after 15 minutes
(measured cold start: **31.4s**; warm: **0.2s**), the instance has 512MB so the
reranker stays off in production, and the LLM budget is a single shared $3/day pool
with no per-user caps. A portfolio reviewer arriving at 3am Pacific hits a cold
start. That is the single highest-risk moment in the whole product.

### The organising principle

**Everything on the reviewer's path must be flawless. Everything off it is
secondary.** For a recruiter that path is short and unforgiving:

```
live link (probably from a resume, possibly on a phone)
      -> page loads FAST and looks professional
      -> understand what this is, in ~15 seconds
      -> see convincing output WITHOUT granting mic permission
      -> maybe try it
      -> leave
```

Three consequences that drive the whole plan:

1. **Assume they never grant microphone permission.** This is the biggest single
   planning assumption. A recorded answer is the core interaction and a recruiter
   on a work laptop, in an open-plan office, very often will not speak into it. If
   the product only impresses after you record, most reviewers see nothing. **There
   must be a compelling no-microphone path** (section 4, B2).
2. **Assume mobile.** Links from a resume get opened on a phone. Every screen on
   the path above has to hold up at 390px.
3. **They will not read the code.** Retrieval architecture, cost accounting and
   test coverage are invisible to this audience. That does not make them worthless
   — they are what you *talk about* in an interview — but they do not earn a place
   on the critical path.

Work that does not touch that path is deprioritised regardless of how interesting
it is.

### What the research says a portfolio project needs

From competitive and hiring research done 2026-08-27/28 (sources at the end):

- *"Wrappers are not portfolio material. Real applications are."* CodeEcho is
  genuinely not a wrapper — hybrid pgvector + full-text retrieval with RRF fusion,
  cross-encoder rerank, an append-only interview log with derived cursors, real
  cost accounting. **None of this is visible to a reviewer today.**
- *"Make AI transparent — show sources, confidence, and cost controls — so your
  project signals engineering judgment rather than a gimmick."* Still the most
  actionable finding, **but read it through a recruiter's eyes**: they cannot judge
  a retrieval pipeline. What they *can* judge is whether the feedback looks specific
  and earned rather than generic. So the transparency work is worth doing for the
  parts that are legible without technical background — a visible rubric, an
  evidence quote, a reference answer — and not for the parts that only an engineer
  would appreciate.
- *"Include metrics."* There are good ones already: 31.4s -> 0.2s cold start,
  ~5s -> ~1s on generation via `thinkingBudget: 0`, a 7x correction in cost
  accounting. They appear nowhere a reviewer would see them.
- *"A live demo, a clean repo, and a write-up a hiring manager can read in under
  five minutes."* The repo is part of the deliverable, not packaging around it.

### Competitive position (keep this framing)

| Product | SWE-specific rubric | Delivery metrics | Voice-first | Free |
|---|---|---|---|---|
| Yoodli | no | **yes** | yes | 5 sessions |
| Final Round AI | partial | no | live copilot, not practice | no |
| Google Interview Warmup | no | word counts only | yes | **retired Apr 2026** |
| interviewing.io | **yes** (human) | no | yes | no |
| Exponent / Pramp | **yes** | no | yes | peer mocks |
| Hello Interview | **yes** | no | no (text) | partial |
| **CodeEcho** | **yes** | **yes** | **yes** | **yes** |

No competitor found does SWE-specific rubrics *and* objective delivery metrics in
one scorecard. Yoodli's standing criticism is that it *"coaches how you speak, not
what you say."* That intersection is the whole pitch and the homepage never says it.

---

## 2. Current state

### Branch `feat/accounts-budget-and-keepalive` — 5 commits, unmerged

```
62f0197  Use the shared analysis hook in practice instead of a second copy
8441e81  Let people resume an interview and revisit past reports
ce0012b  Bill LLM calls from reported tokens instead of guessing at them
47c6689  Stop limiting users; bound the caches that relied on the app sleeping
bfc49bf  Add accounts, durable persistence and progress history
```

`master` is at `a4ca085` and **production runs that**, i.e. everything above —
accounts, persistence, progress, resume, metering, cache bounds — is undeployed.

To ship:

```
git checkout master && git merge --ff-only feat/accounts-budget-and-keepalive && git push
```

That push triggers `og-refresh.yml` (commits a new homepage screenshot) and a Vercel
deploy. Render redeploys the backend separately. **Watch for a window where the
frontend has shipped and the backend has not** — the Resume button calls
`GET /interviews/{id}/current`, which does not exist on the old build.

### Already live (verified)

- **Keep-alive.** Supabase `pg_cron` + `pg_net` job `codeecho-backend-keepalive`,
  `*/14 15-23,0-6 * * *` UTC (= 08:00–23:59 Pacific), 55s timeout. Confirmed with
  five consecutive `succeeded` runs. See `supabase/keepalive.sql`.
- **Render env vars.** `API_BUDGET_CAP_USD=2.50`, `USER_DAILY_CAP_USD=0`,
  `GUEST_DAILY_CAP_USD=0`. See section 0 — the last two are actively harmful until
  the branch deploys.

### Verified vs assumed

Be honest about this when continuing.

| Claim | Evidence |
|---|---|
| Backend behaviour (34 tests) | pytest, green |
| Resume contract | 5 tests + a live start -> history -> resume run |
| Cost metering | 7 tests, incl. the 7x undercount case |
| Types and lint | `tsc --noEmit` and `eslint` clean |
| Keep-alive fires | `cron.job_run_details`, 5 successes |
| **UI renders correctly** | **NOT verified visually.** Chrome extension could not attach to localhost (`document_idle` never fires on the Next dev page). Pages return 200 with correct SSR content and no runtime errors, but no one has looked at the history panel or the refactored practice page. |
| **Practice flow still works end to end** | **NOT verified interactively.** The refactor was walked path-by-path against the original, but nobody has recorded an answer and watched a scorecard appear. |

**Do this before anything else in section 4:** record one practice answer and run
one full mock interview by hand.

---

## 3. Priorities

Ordered by impact on the five-minute path. Complexity is rough dev effort.

Re-ranked for a recruiter reviewer on a two-week deadline. This differs from a
generic "make it good" ordering: everything an engineer would value but a recruiter
cannot see has moved down.

| # | Workstream | Impact | Complexity | In scope? |
|---|---|---|---|---|
| A | Ship the branch, verify the demo path by hand | Blocking | S | **yes** |
| B | Homepage that explains the product | **Highest** | M | **yes** |
| B2 | **No-microphone demo path** | **Highest** | M | **yes** |
| D | No dead ends, no silent failures | High | M | **yes** |
| E | Cold start never looks broken | High | S–M | **yes** |
| M | Mobile pass at 390px | High | S–M | **yes** |
| C | Transparency — visible rubric, reference answer, retry diff | Medium–High | M | **partial** (C1, C2, C4) |
| G | README rewrite | Medium | S | **yes** (README only) |
| H | CI | Low for a recruiter, high for you | S | stretch |
| F | Curated question bank | Medium | L, needs your data | **cut** — see section 5 |

---

## 3a. Two-week schedule

Target 2026-09-11. Ordered so that if you run out of time, you stop at a coherent
point rather than mid-feature. Everything in week 1 is worth more than everything in
week 2.

**Week 1 — make it correct, fast and comprehensible.**

| Day | Work |
|---|---|
| 1 | **A.** Merge, deploy, fix section 0. Hand-verify practice, a full interview, and resume. Fix whatever that surfaces. |
| 1–2 | **D.** Nav links to Practice/Interview, delete or gate `/test`, sweep for invisible errors. Fast and removes the obvious embarrassments. |
| 2–4 | **B.** Homepage rewrite. The single biggest win. |
| 4–5 | **B2 (1).** Static sample scorecard on the homepage, from real frozen output. |
| 5 | **E.** Cold-start skeleton and honest "waking the free backend" copy. |

**Week 2 — make it convincing.**

| Day | Work |
|---|---|
| 6–7 | **B2 (2).** The worked-example route. |
| 8–9 | **M.** Mobile pass at 390px across the critical path. |
| 9–11 | **C1, C2, C4.** Reference answer shown beside the score; rubric shown before answering; per-dimension retry diff. |
| 12 | **G.** README rewrite — demo link, differentiator, real metrics. |
| 13 | Buffer. Something will overrun. |
| 14 | Final pass: click every route on production, on desktop and phone, from a logged-out browser with a fresh guest token. |

**If you fall behind, cut in this order:** C4, then C2, then B2 (2), then M. Never
cut A, D, B, or B2 (1).

---

## 4. Workstreams

### A. Ship and hand-verify — do first

Fixes section 0 and unblocks everything.

1. Merge and push. Watch both deploys.
2. Confirm `/api/budget` reads `cap_usd: 2.5, spent_usd: <real>`.
3. Confirm question generation is no longer hitting the mock bank.
4. **By hand:** record one practice answer end to end; run one full mock interview
   including a follow-up and the final report; start an interview, close the tab,
   reopen `/interview`, hit Resume.
5. Fix whatever that surfaces before starting B.

**Done when:** a stranger can complete practice and a full interview on production
without hitting an error.

---

### B. Homepage that explains the product

**Why.** Today `/` is an intro animation into a mode-select. It never states what
CodeEcho does, who it is for, or why it differs from every other AI interview tool.
For a portfolio piece this is the highest-leverage screen in the app, and it is
currently the weakest.

**Build.**

- A one-line proposition above the fold: you answer real SWE interview questions out
  loud, and it scores **both** your reasoning and your delivery. The two-axis claim
  is the differentiator — say it.
- **A real scorecard visible without recording anything.** A static, honest sample.
  A reviewer who will not grant mic permission still needs to see the output. This
  is probably the single highest-value element on the page.
- Three proof points, concrete not vague: rubric-scored per dimension with evidence
  quotes; delivery measured objectively (fillers, WPM, pauses, idea transitions);
  grounded in a retrieval corpus rather than a bare model opinion.
- Keep the hand-drawn sketch system. It is genuinely distinctive and a real asset —
  do not flatten it into another Tailwind landing page.
- Preserve `warmBackend()` on mount (`frontend/src/lib/api.ts`). It is what makes
  the cold start overlap the reading time.

**Watch out.** The homepage is screenshotted by `.github/workflows/og-refresh.yml`
for the OG image, so redesigning it changes link previews. Check the result.

**Done when:** someone who has never heard of it can state what it does and how it
differs, after 15 seconds, without scrolling.

---

### B2. The no-microphone demo path — highest new priority

**Why.** This is the assumption most likely to decide whether the project lands. A
recruiter clicking a link from a resume, on a work laptop, often in an office, will
frequently decline the mic prompt — and today CodeEcho shows nothing of value until
you have recorded an answer. Every differentiator lives behind that permission
dialog. Fixing this is probably worth more than every other item except shipping.

**Build, in increasing order of effort — the first is the minimum.**

1. **A static sample scorecard on the homepage.** Real, honest output from a real
   answer, rendered with the actual `ScorecardGrid` so it cannot drift from the
   product. Zero interaction required. Minimum viable version of this workstream.
2. **A "See a worked example" route.** A pre-recorded answer with its real
   transcript, delivery metrics and scorecard, played back through the existing
   components. Shows the whole loop — question, answer, delivery analysis, rubric
   scoring — with nothing to grant and nothing to wait for.
3. **Optional: file upload as a first-class alternative.** `FileUpload` already
   exists in `AudioInput.tsx` and is a tab on the practice screen. Surfacing it as
   an equal option rather than a secondary tab gives a reviewer a mic-free way to
   actually run the real pipeline.

**Where the data comes from.** Record one genuinely good answer and one mediocre one
yourself, run them through production, and freeze the resulting JSON as fixtures.
Use real output — a fabricated scorecard will read as fake and undo the credibility
the feature exists to build.

**Done when:** a reviewer who declines the mic prompt still sees a transcript,
delivery metrics and a rubric-scored answer within 15 seconds of landing.

---

### M. Mobile pass at 390px

**Why.** Resume links get opened on phones. If the homepage or a scorecard is broken
at 390px, that is the entire impression.

**Check specifically:** the homepage and its sample scorecard; `ScorecardGrid`, which
is a grid and the most likely to break; `QuestionSetup` and `InterviewSetup`, which
use large `CircleChoice` circles (230px, 190px, 148px) that will not fit side by side
on a phone; `Timeline` and `TranscriptView`; and the `Nav`. Several pages already use
`overflow-x-hidden`, which can mask horizontal overflow rather than fix it — check
whether content is actually being cut off.

**Done when:** every screen on the critical path is usable and unbroken at 390px.

---

### C. Make the AI transparent

**Why.** Research is unambiguous that showing sources, confidence and cost controls
is what separates "engineering judgment" from "ChatGPT wrapper". Separately, the
top user complaint about this category is *"it scores delivery while missing
technical wrongness"* and *"generic, non-context-aware feedback."* CodeEcho already
defends against both — invisibly. Making the existing machinery visible is the
highest-value work in the plan and most of it is surfacing, not building.

**C1. Show the reference solution the scorer already computed.** `scoring.py`
already instructs the model to recall the optimal solution and score against it,
and `overall_summary` *may* mention it. Meanwhile `model_answer()` is a **second,
separate LLM call** behind a "Reveal model answer" button doing overlapping work.
Make the scorer return the reference as a structured field and show it beside the
score. Two wins: stop paying twice on a $3/day pool, and a *visible* reference is
falsifiable by the user — the only real defence against a hallucinated one silently
corrupting the score.

**C2. Show the rubric before answering.** `behavioral.py` holds every dimension with
descriptions and per-seniority anchors. Users currently record blind and discover
the dimensions afterwards. Pure frontend against data that already exists. Directly
answers the *"scored by AI and never told how"* complaint.

**C3. Show the retrieval grounding.** *(Deprioritised — engineer-legible only.)* The scorer retrieves top-k chunks from a
~1,865-chunk corpus and injects them. Nothing indicates this happened. Even a
collapsed "grounded in N sources" with titles converts an invisible differentiator
into a visible one.

**C4. Per-dimension retry diff.** Practice shows one scalar delta. The useful
feedback is per-dimension: "Result 2 -> 4, but Specificity 4 -> 3." `pick_focus()`
already computes weakest-dimension server-side and the retry UI ignores it. The
retry loop is the core differentiator over one-shot tools.

**C5. Cost transparency.** *(Deprioritised — engineer-legible only. Keep it in
your back pocket as an interview talking point instead.)* `/api/budget` exists and nothing surfaces it. A small
honest "this answer cost $0.004 of a $2.50 daily pool" is *exactly* the "cost
controls" signal the research names, and it is now accurate — `ce0012b` made
metering use real provider token counts, including reasoning tokens.

**Done when:** a reviewer can see what the score was based on, what standard was
applied, and what it cost — without reading the source.

---

### D. No dead ends, no silent failures

**Why.** On a portfolio piece a dead link reads as carelessness and undoes the
engineering story.

Known issues:

- **`Nav.tsx` has no links to Practice or Interview**, and Progress renders only
  when `authEnabled`. From `/practice` there is no way to reach `/interview` except
  the browser back button. This is the worst one.
- **`frontend/src/app/test/page.tsx` (334 lines) ships in production** and calls
  `/api/debug/*`, which is off by default (`ENABLE_DEBUG_ROUTES=false`). An
  unreachable page advertising a debug console. Delete it or gate it behind
  `NODE_ENV`.
- **Audit for more invisible errors.** One was already found and fixed: a too-short
  recording set an error and stayed on the setup screen, which does not render one,
  so the button just looked dead. Assume there are others.
- **`main.py` CORS hardcodes four localhost origins** into the production allowlist.
- **`main.py:41` uses deprecated `@app.on_event`** — warns on every test run.
- **`backend/uploads/` grows unbounded** (65 files / 13MB locally, no cleanup).
  Durable copies live in Supabase Storage and `storage.ensure_local_audio()` can
  refetch, so local files are safe to reap after analysis.

---

### E. Cold start never looks broken

**Why.** 31.4s of nothing is fatal for a five-minute review, and the keep-alive
window is 08:00–23:59 Pacific — a reviewer in another timezone gets the cold path.

**Do not** extend the cron to 24/7. Pings burn the same free instance-hours they
protect: 24/7 is ~744h against a 750h/month allowance, leaving ~6 hours of margin,
and exhausting it means Render *suspends* — a dead demo, which is far worse than a
slow one. Widening to roughly 06:00–24:00 Pacific (~558h) is safe if you want more
coverage.

Instead, **design the wait**:

- A skeleton/"waking up" state rather than a spinner or a hang. Research: users are
  markedly more patient when they can see what is happening and anticipate the
  result.
- Say so honestly — "waking the free-tier backend, ~30s" — and turn the constraint
  into a visible engineering decision rather than a bug. For this audience, that
  reads as judgment.
- `warmBackend()` already fires on homepage mount. Consider firing it from the Nav
  on any route.

---

### F. Curated question bank (hybrid) — CUT for the 2026-09-11 deadline

> Kept here in full because it is still the right call for quality, just not for
> this window. A recruiter cannot distinguish a curated question from a generated
> one, it is the only item gated on you producing data, and it is complexity L.
> Revisit after the deadline. See section 5.

**Why.** Chosen strategy, and it addresses the research finding that *"synthetic
questions cluster around generic patterns and rarely reproduce the specific, weird
follow-ups a real loop throws — which are exactly the parts that separate hire from
no-hire."* `questions.py` already fights this hard (an explicit banned-triviality
list, 15 rotating categories, temperature 0.9) but generation is still the ceiling.

**Approach.** The infrastructure exists — `kb_documents`, pgvector, hybrid RRF
retrieval, `scripts/ingest_kb.py`. Extend it to hold questions as a distinct `kind`,
retrieve first, generate on miss.

**Bonus:** retrieval is faster *and* cheaper than generation. On a $3/day shared
pool that matters directly.

**What is needed from you:** roughly 150–300 real questions, tagged by
type/track/bucket and difficulty. Blind 75 / NeetCode-style for coding; real
behavioral prompts for the buckets in `behavioral.py`. Ingestion, dedup and tagging
can be built around whatever format is easiest for you to produce.

**Complexity: L**, and it is the one item gated on you rather than on code.

---

### G. The repo as artifact

**Why.** A recruiter will not read the source, but a non-trivial fraction click the
GitHub link and skim the README — it is the second landing page. Fix the README
because it is cheap and currently misleading; the rest of this workstream is for
your own benefit and for engineer interviewers later, not for the deadline.

- **`README.md` is stale and does not sell.** It still claims a `$5` cap (actually
  `$2.50`), "Gemini transcription with Azure fallback" (it is Azure Whisper only —
  `transcription_configured` *is* `whisper_configured`), and a v2 checklist whose
  items — auth, persistence, progress — are all now done and still unchecked.
  Rewrite it to lead with the demo link, the two-axis differentiator, and the
  metrics.
- **`ARCHITECTURE.md` is genuinely strong** and is an asset — but it says answers
  cap at 90 seconds. Real caps are 180s behavioral/coding and 300s design/project
  (`models.py:answer_cap_sec`, `types.ts:recordingCapSec`). Same stale figure in a
  comment at `routes.py:55`.
- **`backend/.env.example`** drifted from `config.py` before and is worth a pass.

---

### H. CI

Nothing runs `pytest`, `tsc` or `eslint` today; the only workflow is
`og-refresh.yml`. Every doc-drift item in G exists because nothing checks. A
`react-hooks/refs` error in `practice/page.tsx` also sat unnoticed until a lint run
during the refactor. ~25 lines of workflow.

---

## 5. Deliberately not doing

- **F, the curated question bank — cut for this deadline.** It is complexity L, it
  is gated on you producing data, and a recruiter cannot tell a curated question
  from a generated one. The existing anti-triviality guards in `questions.py` are
  good enough for a demo. Revisit after 2026-09-11 — it remains the right call for
  quality, just not for this two-week window.

- **Real-time / conversational interviewer.** Where the category is heading, but it
  breaks the free-tier constraint and the turn-based flow is not the weak point.
- **TTS reading questions aloud.** Nice realism, off the critical path.
- **Scorecard permalinks / sharing.** Real gap, but growth-oriented, and the goal is
  not growth.
- **Anything requiring paid infra.** Reconsider only if the budget answer changes.

---

## 6. Traps — hard-won, do not rediscover

1. **`record_cost()` writes to production Supabase.** It checks
   `supabase_client.is_configured()` first and returns *before* touching the local
   JSON ledger. `backend/.env` has `SUPABASE_URL`, so any ad-hoc script calling it
   hits the live `api_usage_daily` table. This already happened once and wrote **$19
   of fake spend** that had to be cleared by hand. `data/budget_ledger.json` is the
   *offline fallback only* — resetting it cleans nothing when Supabase is set. For
   experiments, set `supabase_client.is_configured = lambda: False` **before**
   importing anything that bills.
2. **`frontend/.env.local` points `NEXT_PUBLIC_API_URL` at production.** Local
   `npm run dev` talks to the live backend unless you override the env var on the
   command line.
3. **For hermetic local runs**, start the backend with `GEMINI_API_KEY=""` and
   `SUPABASE_SERVICE_ROLE_KEY=""` — mock questions, in-memory store, no spend, no
   production writes.
4. **Node runs x64 under Rosetta while the Mac is arm64.** `node_modules` had the
   arm64 Tailwind oxide binding, which broke `next dev` entirely. Currently patched
   with `npm i @tailwindcss/oxide-darwin-x64 --no-save`; a plain `npm i` reverts it.
5. **The Chrome extension cannot attach to the Next dev server** — `document_idle`
   never fires, so screenshots and `read_page` time out. Verify UI by hand or
   against a production build.
6. **Render's `update_environment_variables` merges by default** (`replace: false`).
   With `replace: true` it would wipe every secret on the service.
7. **`cron.job_run_details` has no `jobname` column** — join to `cron.job` on
   `jobid`.
8. **The backend is single-worker on purpose.** Main-question prefetch and the
   in-memory caches depend on it. Do not add workers.
9. **Caches are LRU-bounded now** (`bounded_cache.py`). Before, the 15-minute
   spin-down was the only thing reclaiming them; keeping the service warm made the
   bound mandatory rather than optional.
10. **Debug routes are off by default and must stay off in production.** They are
    unauthenticated and would let anyone drain the LLM budget.

---

## 7. Open questions

Answered on 2026-08-28: reviewer is a **recruiter**; deadline is **~2026-09-11**;
the question bank is **cut** for this window. Remaining:

1. **Keep-alive window.** Currently 08:00–23:59 Pacific. Recruiters may click from
   any timezone, and a cold start is now the top risk to the whole demo. Widening to
   ~06:00–24:00 Pacific costs ~558h/month against the 750h allowance and is safe.
   **Recommend widening.** Do not go 24/7 — see section E.
2. **Sample-answer fixtures for B2.** Record one strong and one mediocre answer,
   run them through production, and freeze the output. Nobody else can produce
   these; they have to be your voice and a real result.
3. **Does the resume link point at `trycodeecho.vercel.app`?** If a custom domain is
   coming, set it up early — DNS and the OG image cache both take time to settle.

---

## Sources

Competitive: [FavTutor](https://favtutor.com/best-ai-mock-interview-tools-2026/) ·
[Mocky](https://mocky.pro/en/blog/ai-mock-interview-tools-compared) ·
[IGotAnOffer](https://igotanoffer.com/blogs/tech/best-mock-interview-websites) ·
[Hello Interview](https://www.hellointerview.com/) ·
[interviewing.io](https://interviewing.io/) ·
[Exponent](https://www.tryexponent.com/practice) ·
[Reddit synthesis](https://ophyai.com/blog/interview-tips/ai-interview-assistant-reddit) ·
[PracHub](https://prachub.com/resources/7-best-ai-mock-interview-platforms-in-2026-ranked-by-real-engineers)

Portfolio: [DEV](https://dev.to/devraj_singh7/the-portfolio-projects-that-actually-get-you-hired-in-2026-1l0e) ·
[Medium](https://medium.com/@ashusk_1790/portfolio-roadmap-2026-5-projects-that-get-interviews-ddcb9716b46b) ·
[Nucamp](https://www.nucamp.co/blog/top-10-full-stack-portfolio-projects-for-2026-that-actually-get-you-hired)

Perceived performance: [LogRocket](https://blog.logrocket.com/ux-design/skeleton-loading-screen-design/) ·
[Simon Hearne](https://simonhearne.com/2021/optimistic-ui-patterns/) ·
[UX Collective](https://uxdesign.cc/what-you-should-know-about-skeleton-screens-a820c45a571a)

Infra: [Odown](https://odown.com/blog/how-to-keep-a-render-free-service-from-sleeping/) ·
[Render community](https://render.discourse.group/t/will-using-cron-jobs-to-hit-free-tier-web-service-every-13-14-minutes-use-up-my-free-instance-hours/23630)
