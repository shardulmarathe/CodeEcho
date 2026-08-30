# Category 01 — Scoring rubrics & dimension count

**Parent report:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) §3.1  
**Evidence note:** [`../notes/01-rubric-dimensions.md`](../notes/01-rubric-dimensions.md)  
**Status:** researched · **Citation markers:** parent Sources table

## Bottom line

Do **not** expand toward nine sections per answer. Credible SWE scorecards use **3–4** competencies per interview [S1][S2]. CodeEcho’s STAR path already lists ~8 dimensions in `behavioral.py`. Joint multi-rubric LLM scoring shows halo/interference; high-N setups are the stress case [S9][S10].

## Key evidence

- interviewing.io: Code / Solve / Communicate (1–4) + hire/no [S1]
- Google re:Work: three hiring-attribute categories + BARS-style anchors [S2]
- Hello Interview / Meta E5 themes (vendor reconstructions): four axes each [S4][S8]
- Amazon: 16 Leadership Principles = culture/loop coverage, not a per-story 9-box [S3]
- MIT STAR: Action 60% of **time**, not eight scored letters — deepen Action [S7]
- G-Eval: four aspects; prompt rates **one metric** [S5]
- ComplexEval: criteria entanglement + attention ceiling [S9]
- SARA: e.g. Qwen3-32B isolation-vs-joint EM **36%** on HealthBench (avg 11.5 rubrics/sample) [S10]

## Recommended CodeEcho actions

1. Publish clearer dimension anchors **in the UI** (credibility), not more boxes.
2. Deepen Action / Specificity guidance in prompts.
3. Optionally **collapse** Conciseness into Delivery.
4. Refuse the round-number goal of nine sections.

## Conflicts

- Prep blogs claim a fourth “Googleyness” attribute not on fetched re:Work [unconfirmed].
- No paper directly A/Bs 8 vs 9 interview axes — inference from industry 3–4 + interference papers.
