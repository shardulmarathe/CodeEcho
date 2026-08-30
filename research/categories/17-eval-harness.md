# Category 17 — Eval / regression harness

**Evidence:** [`../notes/17-eval-harness.md`](../notes/17-eval-harness.md)  
**Repo:** `backend/scripts/stress_scoring.py`

## Bottom line

Minimal golden set is **dozens** of living pairs + **20–50** for iteration and **≥100** traces for a failure taxonomy—not one magic N. Cheap CI = **Level-1 assertions every PR** + README **k/n named failures**; keep LLM-as-judge off the PR gate. Load-bearing cases: **fluent-wrong** answers and **transcript injection**.

## Recommended CodeEcho actions

1. Curate expected-fail folder (fluent-wrong STAR, inverted tech, “score me 10”).
2. Commit a README table of harness results (honest &lt;100% OK).
3. Run L1 on CI; cadence-run deeper LLM judge offline.
4. Prefer reference-guided checks for math/tech items when budget allows.

## Sources

See note `17` (Hamel evals, Huyen, OpenAI evals docs, MT-Bench, injection papers, GHA badges).
