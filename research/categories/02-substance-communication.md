# Category 02 — Substance / empty communication

**Parent report:** [`../DEEP_RESEARCH_REPORT.md`](../DEEP_RESEARCH_REPORT.md) §3.2  
**Evidence note:** [`../notes/02-substance-depth.md`](../notes/02-substance-depth.md)  
**Status:** researched · **Citation markers:** parent Sources table

## Bottom line

Treat “no substance” as a **free heuristic span layer** (weasel/detail density + question overlap), folded into existing Specificity/Communication—not a new rubric dimension and not a second LLM pass [S14][S15][S16].

## Key evidence

- Google Interview Warmup: patterns, **not** grades [S14]
- Yoodli blogs: fillers/pace/talk time — delivery, not depth [S31]
- Final Round AI “missing metric / thin action”: vendor copy [S32]
- Weasels / CoNLL-2010 hedges [S16]; VAGO detail/vagueness ratio [S15]
- Hedge ≠ emptiness (metric-rich hedged claims can be high-substance) [S16][S17]
- BERTScore weak vs G-Eval-4 on Relevance (ρ 0.312 vs 0.547) [S5]

## Recommended CodeEcho actions

1. Lexicon + number/NE density + question-term overlap → span flags.
2. Align spans to Whisper timestamps; highlight in transcript UI.
3. Optionally inject flagged spans into the **existing** judge prompt as evidence.
4. Skip 9th dimension and skip second LLM substance pass.

## Conflicts

- Yoodli homepage “content” vs blogs that only define delivery.
- Interview transfer of news/opinion VAGO detail is analogical.
- Local NER memory on Render free: **not measured** — start lexicon-only.
