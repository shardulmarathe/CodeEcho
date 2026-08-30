# Category 05 — Free-tier constraints & ROI

**Parent report:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) §3.5  
**Evidence note:** [`../notes/05-free-tier-roi.md`](../notes/05-free-tier-roi.md)  
**Status:** researched · **Citation markers:** parent Sources table

## Bottom line

Platform sleep/pause and silent quota death dominate recruiter demos. **Cost** order: transparency + honest 429/cold-start ≈ $0 ≫ one-prompt rubric polish ≫ Markdown RAG ≫ second grader (~2×) [S25][S26][S13]. **Credibility** ranking elevates showing sources/citations above adding dimensions (see [00-ranked-roadmap](./00-ranked-roadmap.md)).

## Infra facts

| Platform | Constraint | Source |
|----------|------------|--------|
| Render Free | Sleep after 15 min idle; spin-up ~1 min official; 750 instance-hours/mo | [S25] |
| Vercel Hobby | Can pause frontend at 100% included usage | [S26] |
| Supabase Free | 500 MB DB, 1 GB storage, pause after ~1 week idle | [S44] |
| Gemini list (not campus) | Flash ~2.7–3.2× cheaper than Pro on Agent Platform SKUs | [S27] |

Stanford ~$3/day shared ceiling and CodeEcho ~$0.02/attempt are **[unconfirmed publicly]** [S13].

## Portfolio / competitive signals

- Live demo someone can poke/break in ~30s [S45]; short GitHub scan wants live URL + evals/citations/cost [S46]
- From marketing pages: free SWE rubric + delivery + voice gap appears open vs Yoodli / Hello Interview / Final Round [S28][S29][S30]
- Warmup never graded; official URL now tips + Gemini Live [S14][S47]

## Recommended CodeEcho actions

1. Honest wake UX + first-class 429 messaging (no silent mock bank).
2. Prefer $0 credibility UI over 2× grader spend.
3. Keep RAG within free storage; citations must be visible or RAG is invisible spend.
4. Treat Vercel Hobby pause risk as real as Render sleep.

## Implementation hooks (in-repo today)

| Hook | Location | Gap |
|------|----------|-----|
| Backend warm on homepage | `frontend/src/app/page.tsx` → `warmBackend()` | Already starts cold-start early; no user-visible “waking server…” if `/api/health` is slow |
| Warm helper | `frontend/src/lib/api.ts` `warmBackend` | Fire-and-forget; does not surface failure |
| Mock fallback | `backend/app/services/questions.py` | Still falls back to mock bank on budget/LLM failure (logged); UI may not distinguish mock vs live |
| Health payload | `/api/health` | Reports `gemini_configured` etc., not “upstream 429 exhausted today” |

**Smallest free ship for reliability credibility:** surface wake state on first API wait; map 429 / mock-bank paths to an honest banner (“Daily AI budget exhausted — try tomorrow” / “Using offline sample question”).

## Conflicts

- Official Warmup page dated 2025-12-11 vs third-party “April 2026” sunset claims — prefer official [S47].
- Campus Gemini SKUs unread (consumer pricing pages redirect-looped in research).
