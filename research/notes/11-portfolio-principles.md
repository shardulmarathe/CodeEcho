# 11 — Portfolio principles (AI / live-demo)

**Date:** 2026-08-30  
**Worker:** research-worker  
**Scope:** Checkable principles for a strong AI/demo portfolio (free-tier live demos); map each to CodeEcho gaps. Recruiter audience. Does not redo 06/08/09/10/12/13 depths.

## Findings

Two clocks: **~30s live poke** (no clone) vs **~90s GitHub scan**. S45: live link → break it → README what/why → evals → code. S46 90s: RAG+citations, evals, live URL, README-as-spec (problem/arch/eval/cost), observability, errors, numbers. S2 first-party: README features+setup+demo+tests; About **website** + topics.

### Checkable principles (pass/fail) → CodeEcho

| ID | Pass if | Fail if | CodeEcho gap (map only) |
|----|---------|---------|-------------------------|
| **P1 Live URL** | README first paragraph + GitHub About “website” open a working app; no clone required (S2, S45, S46) | Link missing, buried, or 503 | URL exists (`trycodeecho.vercel.app`). **Fail risk:** Vercel `DEPLOYMENT_PAUSED` (S4) or Render ~1 min wake with no in-app state (S5 + cat 07) |
| **P2 30s poke** | Empty/weird input fails **visibly**; reviewer can complete one path in ~30s (S45) | Hang, blank, or silent mock | Wake/429/mock/STT still unnamed (cat 07). Guest `/progress` wall (cat 10) blocks “poke history.” No-mic path = worker 12 |
| **P3 Evals in the scan** | README shows golden-set score **and** failing cases; ideally CI gate (S45, S46, S10) | “It works” / vibes / 20/20 with no failures | No `eval.py` / table / CI eval in README. Pipeline exists; **measurement is invisible** |
| **P4 Citations visible** | Retrieved title+URL+snippet on the score (S46 “citations”; Gunn S1 source attribution; cat 04) | RAG in ARCHITECTURE only | Retrieval meta stripped before scorer (cat 04). Invisible RAG = wrapper-looking spend |
| **P5 Cost + latency printed** | $/request or $/1k tok + p50/p95 somewhere a scanner sees (S45, S46). Numbers need not be impressive | Cap mentioned, no unit cost | README: `$5` cap + ledger. Missing ~$/attempt, p50. Campus ~$3/day and ~$0.02/attempt remain **[unconfirmed]** (cat 05) |
| **P6 README = product spec** | Top: one sentence + screenshot/GIF; then live link; 3–5 “X over Y because Z”; eval + limitations (S2, S45, S46) | Stack list, clone-only Quick Start | README has live link + stack + setup + `$5`. **Missing:** GIF, decisions bullets, eval table, honest fail list. `ARCHITECTURE.md` is the write-up, not the 30s funnel |
| **P7 Named degrade ≠ success** | Mock / budget 429 / cold start labeled; health 200 ≠ LLM live (S10 cycle; cat 07) | Mock bank indistinguishable from live | `questions.py` mock fallback still silent (cat 05/07) |
| **P8 Not a wrapper** | Scoped user problem + non-LLM work + measurement + deploy (S3, S8, S10) | STT + one LLM call, no evals/decisions | **Has** dual-axis (STAR/tech + delivery), budget circuit-breaker, pgvector, two modes. **Scans as wrapper** until P3–P7 are visible |
| **P9 Free-tier honesty** | Sleep/pause/quota produce a named page/banner, not a dead click (S4, S5) | 503 or 60s blank | See failure modes below. Keepalive math = worker 13 |

### Visible in ~30–90s

Live URL that survives a poke (P1–P2). Evals as N/M + named failures (P3; S10: no evals ⇒ stay a demo; S45: 18/20 with fails beats fake 20/20). Citations if you claim RAG (P4). Cost/latency one-liner (P5). README: what → demo → X-over-Y → evals → limits (P6). Resume: impact + decision + URL, not tool names (S45).

### Real app vs wrapper (interview-prep)

S3 [marketing]: Whisper+GPT-4 “summarize the call” = wrapper. S46 red flag: “GPT-4 wrapper, no original work.” S8: cool ≠ production (silent prompt fails, stochastic UX, cost/latency). S10: prompt-only iteration never leaves demo.

Interview-prep **pass** = more than STT→score: two workflows (mock vs practice), non-LLM delivery metrics, structured dims+evidence, visible grounding, Level-1 evals on empty/hallucination/mock-vs-live (pass rate is a product choice — S10), 3–5 defendable decisions (S45; skip fine-tune-first). CodeEcho **has** that substance; the gap is **visibility** (P3–P7), not another model.

### Free-tier modes that kill a portfolio demo

| Killer | Official fact | Demo effect | CodeEcho map |
|--------|---------------|-------------|--------------|
| **Vercel pause** | Production serves `503 DEPLOYMENT_PAUSED`; **does not auto-resume** (S4) | Resume-link is dead | Hobby usage/policy pause (cat 05). Commercial-use Hobby is a policy pause (S4) — keep demo non-monetized |
| **Render sleep** | 15 min idle → spin down; wake **~1 minute**; Render loading page is **browser→service**, not an already-open SPA (S5) | Recruiter’s 30s poke looks hung | In-app “waking…” (cat 07). Keepalive math = 13 |
| **Render hour cap** | 750 Free instance-hours/workspace/month; then **all** Free web services **suspended until next month** (S5) | Demo dark for weeks | Monitor hours; one Free service (cat 05) |
| **Bandwidth / no card** | Exhaust outbound bandwidth without a payment method → Free services **suspended** for the month (S5) | Same | [unconfirmed] whether CodeEcho is near this |
| **Silent quota / mock** | Health 200 + mock questions look like success (cat 07; S10) | Reviewer “breaks” nothing; you look dishonest | Banner mock vs live |
| **Ephemeral disk** | Spin-down **wipes local FS** (S5) | File caps reset | Durable budget if Supabase `api_usage_daily`; JSON is local-only |
| **Render Free PG 30d** | Expires (S5) | Data vanish | N/A — CodeEcho uses Supabase (cat 05 pause is different) |

“Deployed on Vercel” ≠ P1-pass without a pause/wake rehearsal before a resume goes out.

**Rank (this note only; does not replace 00b):** P7+P2 honest states → P3 golden set in README → P4 citation row → P5+P6 cost + funnel → P1 rehearsal. Skip invisible wrapper features.

## Conflicts and uncertainty

- **30s vs 90s:** S45 = live poke; S46 = GitHub scan. Same funnel, different surface — not a numeric conflict.  
- **S45/S46 are secondary** (unsigned curriculum site; Landed is a jobs product **[marketing]**). Principles that also appear in S2/S4/S5/S8/S10 are the ones to rank by.  
- S3 ProjectPro is a **[marketing]** course blog; wrapper example is still checkable.  
- Huyen $0.624/prediction (S8, 2023) is **[stale]**; use the *habit* of printing cost, not that number.  
- Gunn (S1) “five projects” vs S45 “three or four deep” — depth+evals win; CodeEcho is already one deep app.  
- Worker 12 (no-mic) and 13 (keepalive) can change P2/P9; not researched here.  
- UI motion (06) and SEO meta (09) out of scope; LICENSE/topics only as S2 About-box items.

## Quotes

- S45: “a live link they can click, poke, and break in thirty seconds”
- S46: “evals and a live URL … scan for … a live link in about 90 seconds”
- S8: “It’s easy to make something cool with LLMs, but very hard to make something production-ready”
- S10: “unsuccessful products almost always share a common root cause: a failure to create robust evaluation systems”
- S10: “focus exclusively on #3 … prevents them from improving their LLM products beyond a demo”
- S3: “Sure, it works, but it’s a wrapper.”
- S4: “visitors see a 503 DEPLOYMENT_PAUSED error”
- S5: “spins down a Free web service that goes 15 minutes without receiving inbound traffic”
- S45: “The numbers don’t have to be impressive — having them is the signal.”

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://dev.to/klement_gunndu/5-ai-portfolio-projects-that-actually-get-you-hired-in-2026-5bpl | 5 AI Portfolio Projects That Actually Get You Hired in 2026 | 2026-03-07 | secondary | Klement Gunn; RAG attribution, evals, DECISIONS.md |
| S2 | https://docs.github.com/en/account-and-profile/tutorials/using-your-github-profile-to-enhance-your-resume | Using your GitHub profile to enhance your resume | unknown | primary | README + About website + tests + topics |
| S3 | https://www.projectpro.io/article/artificial-intelligence-portfolio/1140 | How to Build an Artificial Intelligence portfolio that gets you hired? | unknown | secondary | [marketing]; Whisper+GPT = wrapper vs scoped system |
| S4 | https://vercel.com/kb/guide/why-is-my-account-deployment-blocked | Why has my account or deployment been paused? | unknown | primary | 503 DEPLOYMENT_PAUSED; no auto-resume; Hobby commercial |
| S5 | https://render.com/docs/free | Free Instances \| Render Docs | unknown | primary | 15 min sleep; ~1 min wake; 750 h; FS wipe; PG 30d |
| S6 | https://ai-tldr.dev/learn/building-ai-apps/ai-career-path/build-ai-portfolio/ | How to Build an AI Portfolio That Gets You Hired | 2026-06-11 | secondary | Wave-A S45; 30s poke + README funnel + cost |
| S7 | https://github.com/landedjobs/ai-engineer-portfolio-projects | ai-engineer-portfolio-projects | ~2026-07 | secondary | [marketing] Landed; 90s scan + red flags |
| S8 | https://huyenchip.com/2023/04/11/llm-engineering.html | Building LLM applications for production | 2023-04-11 | primary | Chip Huyen; cool vs production; cost/latency; [stale] $ |
| S9 | https://github.com/chiphuyen/aie-book | chiphuyen/aie-book | unknown | primary | Eval, RAG, when not to finetune; job-candidate audience |
| S10 | https://hamel.dev/blog/posts/evals/ | Your AI Product Needs Evals | 2024-03-29 | primary | Hamel Husain; evals or stay a demo; Level-1 assertions |
| S11 | https://hamel.dev/ | Hamel Husain’s Blog | index 2026-08-12 | primary | Dates S10; later eval posts not fully read |

## Needs-browser

(none)

## Searched

- AI portfolio project hiring
- hireable GitHub project checklist
- AI wrapper vs product hiring
- Vercel hobby pause portfolio demo
- Chip Huyen AI engineer hiring
- Chip Huyen building AI applications
- Hamel Husain your AI evals
