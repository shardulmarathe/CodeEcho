# Category 03 — Grader architecture & cost

**Parent report:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) §3.3  
**Evidence note:** [`../notes/03-grader-designs.md`](../notes/03-grader-designs.md)  
**Status:** researched · **Citation markers:** parent Sources table

## Bottom line

Keep **one** Gemini Pro structured multi-dimension JSON scorecard. Debate (~4×) and per-trait sequential stacks (~8×) are poor defaults under a shared daily LLM ceiling [S11][S12][S34]. Prometheus-class local judges need ~16 GB VRAM — not Render free 512 MB [S35].

## Key evidence

- Single JSON / G-Eval-shaped scorecard matches CodeEcho [S5][S33]
- MT-Bench: GPT-4 single-answer vs humans **85%** (human–human **81%**) [S11]
- ChatEval debate: +2.5 pp on GPT-4 at default 2×2 turns [S12]
- MTS: 4 traits × 2 turns = **8 calls**; helps weak holistic prompts [S34]
- Reference-guided grading: math failure **70% → 15%** on their swap test [S11]
- Cost sketch (~$0.02/attempt **[unconfirmed]**, linear scaling **[speculation]**): 1×≈150 / 4×≈37 / 8×≈18 attempts per $3 day [S13]

## Recommended CodeEcho actions

1. Keep one Pro scorecard with per-dimension rationale/evidence/suggestion.
2. Embed model/reference answer **in the same call** when useful.
3. Optionally **gate** a second Pro pass for technical/math only.
4. Split content vs delivery as **two JSON sections**, not two Pro judges.
5. Flash-delivery + Pro-substance split is **[speculation]** — unpriced for interviews.

## Conflicts

- 2023 verbosity/position bias magnitudes vs 2026 style-dominant papers [S11][S48][S49].
- No primary interview-product multi-grader engineering writeup found.
