# CodeEcho — implementation backlog

**Date:** 2026-08-30 · **Audience:** recruiter/portfolio · **Constraints:** free tier, visible credibility  
**Merged from:** `categories/00`, `00b`, `00c` + wave A–E research. Evidence lives in category files; this is the build order.

## Do first (resume-link path)

| # | Work | Primary categories | In-repo hooks |
|---|------|-------------------|---------------|
| 1 | Homepage **labeled Sample scorecard** + CTA that is not mic | 12, 11, 14 | `frontend/src/app/page.tsx` |
| 2 | Honest **wake / 429 / mock / STT** banners; capability bits on health | 07, 13, 19, 20 | `warmBackend`, `questions.py` mock fallback, `/api/health`, `/api/budget` |
| 3 | Guest **`/progress`** without sign-in redirect | 10 | `frontend/src/app/progress/page.tsx`, `X-Guest-Token` |
| 4 | Scorecard **how graded** + **sources chips** (empty → rubric-only) | 16, 04 | `ScorecardView.tsx`, `scoring.py` `_retrieve_reference`, types |
| 5 | Tag questions `mock \| generated \| pasted` in API + UI | 20 | `questions.py`, attempt/question models |
| 6 | Privacy blurb before Record; retention/delete honesty | 18 | AudioInput / interview setup |
| 7 | Recorder: priming → recording → review; level/clip meter | 15 | AudioInput components |
| 8 | README: pitch + live link + golden-set k/n; LICENSE + topics | 09, 11, 17 | `README.md`, GitHub settings |
| 9 | ESL disclosure on Delivery; content-first report layout | 21 | Scorecard / delivery UI |
| 10 | Guest token expiry + short signed URL TTL + README trust note | 22 | auth/guests, storage signed URLs |

## Do not (defaults)

| Anti-goal | Why | Cat |
|-----------|-----|-----|
| Expand to ~9 rubric dimensions | Industry 3–4; interference | 01 |
| Default multi-grader / debate | 4–8× cost | 03 |
| Always-on Render keepalive | Nearly exhausts 750h | 13 |
| Silent mock bank as live LLM | Demo killer | 07, 20 |
| Ingest Hello Interview / interviewing.io | ToS | 04, 14 |

## Research pointer

Full evidence: [`INDEX.md`](./INDEX.md). Wave F implications: [`categories/00d-wave-f-roadmap.md`](./categories/00d-wave-f-roadmap.md). Archived brief: [`archive/nextsteps-2026-08-28.md`](./archive/nextsteps-2026-08-28.md).
