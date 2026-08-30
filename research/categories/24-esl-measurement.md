# Category 24 — ESL / delivery bias measurement

**Evidence:** [`../notes/24-esl-measurement.md`](../notes/24-esl-measurement.md)  
**Extends:** category 21 (disclosure / content-first)  
**Flags:** no NIST accent-fairness standard; L1/L2 WER direction conflicts by dataset

## Bottom line

There is **no NIST accent/speech-fairness standard** (OpenASR is low-resource languages). Use NIST AI RMF MEASURE 2.11 plus IEEE 7003 **abstract/scope** guidance (full PDF unread this pass), and measure with **public labeled corpora** (Fair-Speech, Artie) plus **mixed-effects Poisson on error counts** (Liu et al.) — not raw subgroup WER means and not production users’ protected-class labels. Filler/WPM “bias” often means **ASR contamination** or **fluency construct**; interpret gaps in three layers before shipping “fixes.”

## Protocol (one-time offline audit)

1. Run production ASR + Delivery heuristics on Fair-Speech and Artie (optional L2-ARCTIC for ASR only — read speech is weak for pause/filler construct).
2. Per utterance log: WER, WPM/fillers/pauses on **gold and ASR**, SNR, confidence; aggregate **per speaker**, then subgroup.
3. Fit Liu-style Poisson with `log(n_words)` offset and speaker random effect (Herron: ~35 speakers/SG under δ̂=0.1, σ=0.15, one-sided 95%/power 0.8 — not a universal n).
4. **Three-layer read:**
   - **A** WER(L2)>WER(L1) → Delivery on ASR is contaminated  
   - **B** gold WPM/pause L2≠L1 → construct (disclose; don’t equalize blindly)  
   - **C** ASR−gold filler Δ larger for L2 → measurement bias → disclosure + transcript edit (cat 21)

## Do not

- Compare raw mean WER across L1/L2 without speaker averaging / confounders (Herron: Fair-Speech “L2 better” is ethnicity-confounded).
- Collect accent/L2 labels from CodeEcho users for a demo audit.
- Treat gold-transcript fluency gaps as detector bugs.

## Recommended CodeEcho actions

1. Keep cat-21 ESL disclosure on Delivery until/unless an offline audit is run.
2. If auditing once: Fair-Speech + Artie offline; log schema above; report A/B/C layers in README.
3. No published filler-F1×L2 table — do not claim measured filler fairness without generating that table yourself.

## Sources

See note `24` (S1–S17).
