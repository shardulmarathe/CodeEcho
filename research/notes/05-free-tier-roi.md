# 05 — Free-tier ROI for CodeEcho improvement classes

**Worker scope:** constraint economics + recruiter-visible positioning. Not rubric science, substance methods, grader papers, or corpus recipes.

**CodeEcho costs:** ~$0.02/attempt and Stanford ~$3/day LLM are given background only [unconfirmed] — no public CodeEcho or Stanford quota page verified.

## Findings

- **[S1 primary] Render Free sleep dominates the 30–60s recruiter path.** Idle 15 min (HTTP + existing WebSocket messages). Next request/new WS: official spin-up "about one minute"; Render shows a loading page. Local FS lost on spin-down. Official ~60s vs CodeEcho-measured ~31s: same class; both can consume a recruiter glance if the *first* click hits a sleeping API. 750 Free instance-hours/workspace/month; running services consume hours, spun-down do not; exhaust → all Free web services suspended until next calendar month. No card + bandwidth overage → all Free services suspended. Render may restart Free web anytime. Free Postgres: 1 GB, 30-day expiry (+14-day grace then delete), no backups, one Free DB/workspace. **Keep-alive is not a free lunch:** one always-on instance ≈ 24×30 = 720h vs 750h cap — thin margin; two always-on Free webs would exhaust. Do not treat ping-SaaS blogs as primary.

- **[S2+S2b primary] Vercel Hobby can pause the *frontend*, not just slow it.** Hobby: personal/non-commercial. Included (S2): 1M function invocations, 4 CPU-hrs, 360 GB-hrs, 50k Web Analytics events/mo; 100 GB Fast Data Transfer and 1h runtime logs (S2b). Exceed most limits → wait ~30 days. **At 100% included usage, Hobby is paused; Pro is not auto-stopped** (S2b, updated 2026-08-11). Recruiter-visible failure: site dark, not a slow grade. Silent quota death is the twin of Render sleep.

- **[S3+S3b primary] Supabase Free is enough for small session/RAG metadata, hostile to "always-on + bigger ingest."** $0; two free projects (paused do not count) (S3b, 2026-08-28). Per pricing: 500 MB DB/project; 1 GB storage; 5 GB egress; 50k MAU; 500k Edge Function invocations; 2M Realtime msgs; 200 peak connections; no automatic backups; **pauses after 1 week of inactivity** (S3). Larger RAG ingest hits DB/storage/egress before "smarter chunks." Idle pause is a second cold-start sibling if the live app depends on unpaused Supabase.

- **[S5 primary] LLM class costs (Google Cloud Agent Platform list prices, USD / 1M tokens, standard ≤200K).** Gemini 3.7 Flash intro through 2026-12-31: $0.75 in / $3.75 out; from 2027-01-01: $1.50 / $7.50. Gemini 3.1 Pro Preview: $2.00 in / $12.00 out (long-context $4 / $18). **Pro vs Flash intro ≈ 2.7× input, 3.2× output.** 2.5-era: Pro $1.25/$10 vs Flash $0.30 in (output in same table, not re-fetched in tail). 4xx/5xx (incl. many 429s) are **not billed** on this page — they still burn user time and may burn campus daily caps. Stanford $3/day and Gemini *API* (ai.google.dev) list prices were **not** fetched (redirect loop, exit 4). Ratios are a proxy, not campus SKUs.

- **Idea-class cost order (cheap → expensive), $0 spend assumed:** (1) frontend transparency of *existing* scores/links/limitations + honest 429/cold-start + no-mic/type path; (2) more rubric fields in **one** prompt (extra rubric text + extra JSON/rationale tokens, **one** RTT); (3) larger RAG ingest (S3 storage/egress + more retrieved tokens per grade — worker 04 owns recipes); (4) second grader pass ≈ **~2× calls, ~2× latency, ~2× daily-cap risk**. Substance/empty-sentence: local heuristic sits with (1); extra LLM pass sits with (4). Do not invent CodeEcho token counts.

- **Recruiter-visible impact order (high → low) for a 30–60s visit:** (1) **demo actually runs** — no silent mock, visible wake/429, type-without-mic (voice-first competitors imply a mic gate; Yoodli’s loop is speak → speaking report [S8 marketing]); (2) **transparent specific feedback vs wrapper** — live URL, evals, decisions, cost/latency, honest failures [S6, S7]; (3) more dims **if the UI shows them**; (4) RAG quality (invisible unless citations/links); (5) multi-grader (invisible unless disagreement is shown; extra wait hurts the visit). Practice-user ranking puts substance-heuristic and RAG citations higher than recruiter 30s, still below honest uptime.

- **[S6 secondary] AI/TLDR (2026-06-11):** hiring managers click a live link they can "poke, and break in thirty seconds"; funnel ≈ 5 min: live link → try to break (empty/weird input) → 30s README → evals → readable code. Highest-leverage add is measurement + shown failures, not more model calls. Cost/latency numbers are "senior signals." Opaque scores fail this funnel.

- **[S7 secondary] Landed catalog (updated 2026-07):** ~90s GitHub scan; they do not clone. Ordered signals: production RAG + **citations**, eval suite, **live URL**, README as product spec (problem, arch, eval numbers, **cost**), observability. Aligns with showing grade *why* + links over a second hidden judge.

- **Competitive positioning (product pages; flag [marketing]):** **Yoodli [S8]** — role + follow-ups + "speaking report" (pacing, filler words); also "use during your interview" private nudges. Delivery-strong, SWE-rubric-weak; live-nudge is recruiter-hostile if used in a real loop. **Hello Interview [S9]** — SWE curriculum (system design, coding, LLD, behavioral); Premium $47 / $79 / $279; "100,000+" engineers; free learn, not a free voice+delivery+rubric demo. **Final Round AI [S10]** — Interview CoPilot listens live and streams private answers; Stealth "on by default"; live CoPilot is paid ($25+/mo); Free is Goals/prep only. CodeEcho should not compete on stealth; honest practice + visible rubric is the opposite signal. **Google Interview Warmup [S11 primary]:** `grow.google/interview-warmup` now serves "How to Prepare for an Interview" (dated 2025-12-11), pointing to **Gemini Live** and Career Dreamer — not a scoring warmup. Structured free voice-drill niche is vacant at that URL. Third-party "April 2026 shutdown" posts conflict with the Dec 2025 article date (see Conflicts).

- **Highest-leverage free wins (synthesis, not a new source):** ship honest wake/429 UX and a no-mic path before buying tokens; surface existing rubric evidence, citations, cost/latency, and limitations on the homepage/results (S6/S7); expand dims in the **same** Flash-class call if the UI will show them; treat RAG growth as practice-user + citation-UI, not recruiter bait; treat multi-grader as last under a ~$3/day cap unless the second pass is async and disagreement is displayed. Keep-alive only if the workspace has **one** Free web service and hour headroom is monitored (S1).

## Conflicts and uncertainty

- Render official wake ~1 minute vs CodeEcho ~31s vs vendor blogs 30–90s — same failure mode, different clocks.
- Interview Warmup: official URL is a Dec 2025 tips article [S11]. Competitor blogs (not fetched as primary) claim April 2026 retirement. Exact sunset month unresolved; product is gone from the official path.
- Gemini consumer API (`ai.google.dev/pricing` and `/gemini-api/docs/pricing`) exit 4 (redirect loop). S5 is Vertex/Agent Platform list price, not Stanford campus billing.
- Stanford ~$3/day and CodeEcho ~$0.02/attempt [unconfirmed].
- AI/TLDR and Landed are career-content orgs, not named hiring managers at FAANG [secondary]. Upskillist/Medium search hits not fetched.
- Yoodli "use during your interview" vs CodeEcho practice-only: competitive contrast is from Yoodli’s own marketing [S8].
- Worker 01–04 own method quality; this note only ranks **classes**.

## Quotes

- S1: "This process takes about one minute."
- S1: "spun-down services don't consume Free instance hours"
- S2b: "Hobby plans will be paused when they exceed the included free tier usage"
- S6: "a live link they can click, poke, and break in thirty seconds"
- S7: "hiring managers scan for observability, error handling, eval rigor, and a live link in about 90 seconds"
- S8: "speaking report with analytics such as pacing and filler words"
- S10: "Stealth Mode 100% invisible." / "There is no free trial - live sessions need an active Pro subscription."
- S5: "You're charged only for requests that return a 200 response code."

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://render.com/docs/free | Deploy for Free – Render Docs | unknown (fetched 2026-08-30) | primary | Official Free web/Postgres limits |
| S2 | https://vercel.com/docs/plans/hobby | Vercel Hobby Plan | unknown (fetched 2026-08-30) | primary | Included usage; pause-after-30-days |
| S2b | https://vercel.com/docs/plans | Account Plans on Vercel | 2026-08-11 | primary | Hobby paused at 100% usage |
| S3 | https://supabase.com/pricing | Supabase Pricing | unknown (fetched 2026-08-30) | primary | Free column; [marketing] framing |
| S3b | https://supabase.com/docs/guides/platform/billing-on-supabase | About billing on Supabase | 2026-08-28 | primary | 2 free projects; quotas |
| S5 | https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing | Agent Platform Pricing \| Google Cloud | unknown (fetched 2026-08-30) | primary | Flash vs Pro list $; not campus API |
| S6 | https://ai-tldr.dev/learn/building-ai-apps/ai-career-path/build-ai-portfolio/ | How to Build an AI Portfolio That Gets You Hired | 2026-06-11 | secondary | Named site, not a named HM |
| S7 | https://github.com/landedjobs/ai-engineer-portfolio-projects | Landed AI engineer portfolio catalog README | 2026-07 (badge) | secondary | Vendor-adjacent catalog |
| S8 | https://yoodli.ai/use-cases/interview-preparation | Yoodli AI Interview Coach | unknown | primary / [marketing] | Delivery + live-nudge claims |
| S9 | https://www.hellointerview.com/ | Hello Interview | unknown | primary / [marketing] | SWE content + Premium prices |
| S10 | https://www.finalroundai.com/ | Final Round AI Interview CoPilot | unknown | primary / [marketing] | Stealth live assistant |
| S11 | https://grow.google/interview-warmup | How to Prepare for an Interview \| Grow with Google | 2025-12-11 | primary | Warmup URL → tips + Gemini Live |

## Needs-browser

- `https://ai.google.dev/gemini-api/docs/pricing` and `https://ai.google.dev/pricing`: fetch.py exit 4 (curl 50 redirects). Alternative used: S5 Cloud pricing. Consumer Gemini API SKUs still unverified.
- Render `.md` docs exit 3 (markdown); HTML `/docs/free` worked. No browser used.

## Searched

- Render free tier sleep
- Vercel Hobby plan limits
- hiring manager AI portfolio
- Supabase free plan limits
- Gemini Flash Pro pricing
- Yoodli interview practice features
- Google Interview Warmup status
