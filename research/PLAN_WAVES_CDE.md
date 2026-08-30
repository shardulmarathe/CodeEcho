# Research plan — CodeEcho remaining areas (waves C–E)
**Date:** 2026-08-30 · **Classification:** breadth-first · **Tier:** High · **ROOT:** /Users/shar/Documents/GitHub/CodeEcho

## Question (verbatim)
Yes, lets go through those research areas and you can run as many waves as needed and don't stop once you are done and then report findings in their own .md file

## Interpretation and success criteria
Research all previously listed *remaining* areas (not redoing 01–10). Each area gets its own `research/categories/NN-*.md` backed by a worker note. Audience remains **recruiter/portfolio (A)**; free tier + visible credibility. Multiple waves until the list is exhausted. Update `INDEX.md`. Citation-audit new category files.

## Covered already (do not redo)
01–05 scoring/RAG/ROI · 06–10 UI/reliability/mobile/SEO/auth

## Wave C questions
| # | question | note file | boundary |
|---|----------|-----------|----------|
| 11 | Checkable portfolio/“good AI project” principles mapped to CodeEcho gaps | `notes/11-portfolio-principles.md` | Not UI tokens (06); not SEO meta (09) |
| 12 | Homepage / onboarding / no-mic demo patterns for recruiters who won’t grant mic | `notes/12-homepage-nomic.md` | Not visual craft tokens (06); not auth walls (10) except CTA |
| 13 | Cold-start / perceived-performance patterns fitting Render free + keepalive limits | `notes/13-latency-coldstart.md` | Not error-copy (07); not SEO |
| 14 | Competitive teardown: Yoodli, Hello Interview, Final Round AI, Warmup status — free SWE rubric+delivery+voice gap | `notes/14-competitive-landscape.md` | Not CodeEcho implementation recipes |
| 15 | Voice/recorder UX: levels, countdown, retry, clipping for interview practice | `notes/15-voice-recorder-ux.md` | Not WCAG target sizes (08); not STT error enums depth (07) |

## Wave D questions (after C)
| # | question | note file | boundary |
|---|----------|-----------|----------|
| 16 | UI patterns for “how graded / why / sources” scorecard transparency | `notes/16-scoring-transparency-ux.md` | Not RAG corpora licenses (04) |
| 17 | Free eval/regression harness patterns for LLM scorers | `notes/17-eval-harness.md` | Not multi-grader theory (03) |
| 18 | Privacy / audio retention / storage disclosure for interview demos | `notes/18-privacy-audio.md` | Not exploit guidance |
| 19 | Cost/budget metering UX under shared LLM ceilings | `notes/19-cost-metering-ux.md` | Not Stanford SKU pricing deep dive |
| 20 | Curated vs generated question-bank quality for SWE interview prep | `notes/20-question-bank.md` | Not full curriculum authorship |

## Wave E questions (after D)
| # | question | note file | boundary |
|---|----------|-----------|----------|
| 21 | ESL / non-native speaker bias in delivery metrics & scoring | `notes/21-esl-delivery-bias.md` | Not full i18n productization |
| 22 | High-level guest-token + signed-audio-URL trust boundaries for free demos | `notes/22-guest-audio-trust.md` | Defensive only; no exploit PoCs |

## Known unknowns
- Prior nextsteps.md and categories 00/00b already recommend some of these — research must add *external* evidence, not only restate repo notes
- Competitive ToS already forbid ingesting HI/i.io content (note 04) — teardown is feature/UX only
