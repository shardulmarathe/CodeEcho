# Category 23 — Competitive live UI (try/demo surfaces)

**Evidence:** [`../notes/23-competitive-live.md`](../notes/23-competitive-live.md)  
**Extends:** category 14 (marketing landscape)  
**Flags:** marketing CTAs ≠ product UI; post-login UI unread

## Bottom line

Among Hello Interview, interviewing.io, Final Round AI, Yoodli, and Exponent, **no public scorecard or transcript appears without an account**. Recruiter-clickable “try/free” paths land on **signup/login**. No-login chrome observed: HI problem catalog + behavioral session-length picker, and FRAI `/try` format list (FREE badges) — still no session or scorecard. CodeEcho’s labeled no-mic sample scorecard is therefore a **differentiator vs these public try surfaces**, not parity with their marketing “report/breakdown” promises.

## What was observed (2026-08-30)

| Product | Public without account | After primary try CTA |
|---------|------------------------|------------------------|
| Hello Interview SD Bitly | Catalog + desktop-only banner | Sign In (email/Google) |
| Hello Interview Behavioral | Mode picker (Micro/Mini/Full), Premium-specific Q, TTS toggle | **Start Practice → Sign In** (lead browser) |
| interviewing.io AI Interviewer | Homepage marketing | Redirect to login `nextPath=/interview-ai` |
| Final Round AI `/try` | FREE badges on General + Mock; format list | All CTAs → `/sign-up` |
| Yoodli | Marketing only | **Start roleplaying → `app.yoodli.ai/signup`** |
| Exponent | Marketing | “Create your free account” |

Shared patterns (≥2): free CTA → signup; report/feedback **promised**, never shown publicly; mock-vs-live and AI-vs-human are marketing labels; mic gates and cold-start waits **not** observable without a session.

## Recommended CodeEcho actions

1. Keep (and ship) a **labeled sample scorecard** on the homepage — competitors do not show one publicly.
2. Do not imply competitor parity on “instant AI report” without noting their try path is auth-gated.
3. Guest try without signup remains a portfolio credibility wedge vs HI/i.io/FRAI/Yoodli public paths.

## Known gaps

Post-signup in-app UI (FRAI General/Mock, HI Bitly after account) not observed. Pramp unfetched. Yoodli signup UI browser-gated in headless Chromium.

## Sources

See note `23` (S1–S14).
