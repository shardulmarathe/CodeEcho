# Category 19 — Cost / budget metering UX

**Evidence:** [`../notes/19-cost-metering-ux.md`](../notes/19-cost-metering-ux.md)  
**Repo:** `GET /api/budget`

## Bottom line

Show **remaining vs ceiling before** the wall; name **which** ceiling fired (local ledger vs shared upstream); for known daily caps give a **clock** (“try after DATE 00:00 UTC”), not a spinner. Copy: “shared demo budget (all visitors), not your personal quota.”

## Recommended CodeEcho actions

1. Surface `/api/budget` in UI (progress bar + remaining).
2. Distinct banners: local cap vs upstream 429 vs unexpected 5xx.
3. On mock-bank fallback because of budget/LLM failure—say so.
4. Don’t imply per-user quota when caps are shared.

## Sources

See note `19` (GitHub rate-limit headers, Anthropic/Claude usage docs, OpenAI spend limits, GOV.UK unavailable pages, NN/g system status).
