# Research plan — CodeEcho expansion (wave B)
**Date:** 2026-08-30 · **Classification:** breadth-first · **Tier:** Medium · **ROOT:** /Users/shar/Documents/GitHub/CodeEcho

## Question (user direction, 2026-08-30)
1. Audience: **A** (recruiter/portfolio impression — first 30–60s, live demo, GitHub skim)
2–5. Categories: **UI / visual craft / motion**, **Reliability / error honesty**, **Mobile / accessibility**, **SEO**, **Auth**

## Defaults for unanswered items
- Output: **C** (index + per-category files + short addendum to main report) — matches existing tree
- End state: research this wave; implementation only after reports (user previously leaned B)
- Constraints: free tier + prefer visible credibility + no binding deadline (confirmed earlier)
- Effort: **Medium** — exactly 5 workers for the 5 categories

## Interpretation and success criteria
Produce evidence-backed `categories/06–10.md` + notes, update `INDEX.md`, addendum on `DEEP_RESEARCH_REPORT.md`. Frame recommendations for a **recruiter clicking a resume link**, under $0 infra.

## Questions
| # | question | owner note file | boundary |
|---|----------|-----------------|----------|
| 6 | UI/visual/motion principles for credible craft in ~15–60s on a free interview-prep web app? | `research/notes/06-ui-craft.md` | Not cold-start keepalive math; not SEO meta tags |
| 7 | How should free apps surface sleep, 429, mock fallback, STT failure honestly for recruiters? | `research/notes/07-reliability-honesty.md` | Not paid APM; not visual redesign |
| 8 | Mobile + accessibility free wins for voice interview-prep (resume links on phones)? | `research/notes/08-mobile-a11y.md` | Not native apps; not SEO |
| 9 | Free SEO / discoverability / OG / GitHub-skim signals for a portfolio demo? | `research/notes/09-seo-distribution.md` | Not paid ads; not auth UX |
| 10 | Auth / magic-link / guest / progress UX that increases trust without paid IdP? | `research/notes/10-auth-ux.md` | Not rebuilding auth stack; not SEO |

## Known unknowns
- CodeEcho already has sketch UI, og-refresh workflow, warmBackend, Supabase magic link, guest tokens — research must gap-map to repo, not invent greenfield
- Wave A covered scoring credibility — do not redo rubric/grader science
