# Expansion plan draft — contingent on user answers

**Date:** 2026-08-30 · **ROOT:** `/Users/shar/Documents/GitHub/CodeEcho`  
**Status:** DRAFT only — do not spawn workers until the user answers the direction questions in chat / `INDEX.md`.

## Already done (wave A)

- Synthesis: `DEEP_RESEARCH_REPORT.md` (audited)
- Split: `INDEX.md` + `categories/00–05`
- Notes: `notes/01–05`

## Direction questions (copy answers here when received)

| # | Prompt | Answer |
|---|--------|--------|
| 1 | Audience A/B/C/D | **ACTIVE: A** (recruiter/portfolio) — user 2026-08-30 |
| 2 | New categories list | **ACTIVE:** UI/visual craft/motion · Reliability/error honesty · Mobile/accessibility · SEO · Auth |
| 3 | Output A/B/C | **ACTIVE: C** (default; user did not specify) |
| 4 | End state A/B/C | **ACTIVE: research first**; impl after (default B lean) |
| 5 | Constraints confirm | **ACTIVE: yes** (prior session) |
| 6 | Effort | **ACTIVE: Medium** — 5 workers matching 5 categories |

## Contingent worker packages

When answers arrive, pick packages whose category was selected. Each package → one `research-worker`, one note `notes/NN-<slug>.md`, then one `categories/NN-<slug>.md` written by the lead.

### P06 — Portfolio / “what makes a good project” principles
- **When:** user includes portfolio-principles OR picks audience A/D
- **Objective:** Extract checkable principles for AI portfolio demos (live link, transparency, evals, cost story, README funnel) from hiring/portfolio primary sources; map each to CodeEcho gaps.
- **Out of scope:** UI visual systems; LLM judge science (done).

### P07 — UI / visual craft / motion (free-tier web)
- **When:** user includes UI
- **Objective:** Principles for distinctive, credible product UI without a design system budget; what portfolio reviewers notice in 15s; anti-patterns for AI-slop UIs; motion that signals craft not noise.
- **Out of scope:** Backend latency; RAG.

### P08 — Latency / cold-start / perceived performance
- **When:** user includes latency OR optimization
- **Objective:** Free-hosting cold-start mitigations (keepalive limits, skeleton UI, optimistic warm, edge vs origin); perceived-performance patterns while Render sleeps; what actually fits Render 750h + Supabase keepalive.
- **Out of scope:** Multi-grader cost (done in 03).

### P09 — Reliability / error honesty / observability
- **When:** user includes reliability
- **Objective:** Patterns for surfacing upstream 429, STT failure, mock fallback, budget exhaustion without silent degradation; minimal free observability (logs, health semantics).
- **Out of scope:** New paid APM.

### P10 — Homepage / onboarding / no-mic path
- **When:** user includes homepage OR no-mic
- **Objective:** Evidence for demo paths that work without mic permission; frozen/fixture scorecard ethics; first-viewport information architecture for interview-prep tools.
- **Out of scope:** Full visual redesign (P07).

### P11 — Mobile / accessibility
- **When:** user includes mobile OR a11y
- **Objective:** Mobile interview-prep UX constraints; WCAG-relevant free wins for voice apps; resume-link phone usage patterns if sourced.
- **Out of scope:** Native apps.

### P12 — README / write-up / SEO / distribution
- **When:** user includes README OR SEO OR distribution
- **Objective:** Hiring-manager GitHub skim checklist; README structure for AI demos; OG/preview hygiene (CodeEcho already has og-refresh); SEO only if free/static.
- **Out of scope:** Paid ads.

### P13 — Auth / progress / account UX polish
- **When:** user includes auth
- **Objective:** Magic-link / guest / progress UX patterns that increase trust without paid IdP; what to show on `/progress` for credibility.
- **Out of scope:** Rebuilding auth stack.

## Effort → how many packages

| Tier | Max new workers | Selection rule |
|------|-----------------|----------------|
| Standard | 2–3 | User’s top picks only |
| Medium | 3–5 | Top picks + portfolio-principles if not listed |
| High | 5–8 | All selected; hard cap 8 |

## Output shape (from Q3)

- **A:** write `categories/NN-*.md` + update `INDEX.md` only
- **B:** expand `DEEP_RESEARCH_REPORT.md` sections only
- **C:** both A and a short synthesis addendum in the main report

## Implementation gate (from Q4)

- **A:** stop after audited category reports
- **B/C:** after research, open an implementation goal/pass for top ranks — **not** started from this draft alone

## Next concrete step when answers land

1. Fill the answers table above.
2. Rewrite `PLAN.md` Questions table for wave B.
3. Spawn selected workers in one parallel message.
4. Synthesize category files; citation-audit new claims; update `INDEX.md`.
5. Only then consider UpdateGoal complete (research end-state) or hand off to implementation.
