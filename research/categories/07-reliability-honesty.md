# Category 07 — Reliability / error honesty

**Evidence:** [`../notes/07-reliability-honesty.md`](../notes/07-reliability-honesty.md)  
**Audience:** recruiter · **Repo hooks:** `warmBackend()`, `questions.py` mock fallback, `/api/health`

## Bottom line

Treat wake, 429, mock fallback, and STT failure as **named states**, not silent success. `/health` 200 must not imply the LLM works; unused mock paths are the SRE “code path that doesn’t work” [S1][S6][S9].

## Key evidence

- Worst error = no message; copy must be visible, precise, constructive [S1]
- Render Free: 15 min sleep, ~1 min wake; SPA already loaded can look hung without an app-owned waking state [S2]
- Distinguish 429 vs 5xx vs success; Stripe pattern: typed error + human message + request id [S3][S7][S8]
- GOV.UK: one service-wide banner for delay; shutter page for planned close; problem page + log all for unexpected [S10][S12][S13]
- Health: liveness ≠ readiness; check body even on HTTP 200; optional deps can be down while process is up [S4][S9]
- SRE: 200 + wrong content counts as error; monitor when degraded [S6][S14]
- STT: map typed errors (`not-allowed`, `no-speech`, `network`); don’t trust implementor `message` strings as UI [S11][S15]

## Recommended CodeEcho actions

1. Capability bits on health or first API response: `llm: live|mock|429`, `stt: …`.
2. In-page “Waking free-tier server…” while `warmBackend` / first request is slow.
3. Banner when question came from mock bank or scoring 503’d for budget.
4. Surface request/correlation id on failures for your own logs.
5. Never present mock questions as indistinguishable live LLM output.

## Sources (note-local)

See note `07` Sources S1–S15 (NN/g, Render, MDN 429, Stripe, GOV.UK, SRE, Azure health).
