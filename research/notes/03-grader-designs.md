# 03 — Multi-grader / specialized LLM-judge patterns

Scope: interview/essay-style scoring architectures; agreement/bias/cost vs one structured multi-dimension scorecard; viability under ~$3/day and ~$0.02/attempt (~150 attempts/day theoretical max).

## Findings

### Architectures (documented)

1. **Single JSON / form-fill scorecard (G-Eval; LLM-Eval).** One LLM gets task + criteria, optionally auto-generates CoT evaluation steps, then fills scores per aspect. G-Eval (S1) is the closest published analogue to CodeEcho’s overall_summary + per-dimension score/rationale. LLM-Eval (S2 survey) uses one prompt for content/grammar/relevance/appropriateness. G-EVAL-4 Spearman on SummEval summary-level **0.514**; dropping CoT only to **0.500** (S1 Table 1 “- CoT”). Probability-weighted digits matter more than extra judges. If the API lacks logprobs, authors sample **n=20, T=1** to estimate them (S1) — a 20× call multiplier, not needed if the model emits structured JSON.

2. **Pointwise vs pairwise vs listwise.** MT-Bench (S3) compares pairwise comparison, single-answer grading, and (separately) reference-guided variants. Pairwise is more sensitive to close pairs but needs position swaps; single-answer is “more scalable.” GPT-4 single-answer vs humans on MT-Bench S2 (non-tie): **85%** agreement vs human–human **81%** (S3). Pairwise does not clearly beat a strong pointwise rubric for ranking quality.

3. **Sequential specialized judges (MTS / RMTS / TRATES).** Educational AES, not interview products. **MTS** (S4): ChatGPT decomposes a rubric into **four traits**; the scorer runs **independent conversations per trait**, each **two turns** (quote retrieval, then score); overall = average + min-max + quartile clip. Beats “Vanilla” holistic CoT by up to **+0.437 QWK** on TOEFL11 (0.025→0.462) and **+0.355** on ASAP (0.205→0.560); more traits (2→4) raise QWK (S4 Fig. 7). **RMTS** (S5): **separate LLM agent per trait** writes rubric-tied rationales; a fine-tuned S-LLM (T5/BART/etc.) predicts numeric multi-trait scores (needs labeled essays + GPU). **TRATES** (S6): LLM turns a trait rubric into questions, answers each, then a **classical regression** predicts trait scores — hybrid, not a live multi-judge chat.

4. **Debate / ensemble.** **ChatEval** (S7): homogeneous GPT agents, **diverse personas required**; default **2 agents × 2 discussion turns**, one-by-one, plus position calibration. Vs single-agent: **+6.2 pp accuracy (ChatGPT), +2.5 pp (GPT-4)** on FairEval-style OA; vs G-Eval on dialogue, GPT-4 ChatEval **+0.096 Spearman (16.3%)**. Same-persona debate **does not beat** single-agent (S7 Table 3). Accuracy peaks at **3–4 roles (62.5%)**, drops at 5; extra discussion turns **do not help** (context bloat). Survey (S2) also lists PRD (peer rank+discussion), Auto-Arena committees, PRE weighted peer review, PoLL (panel of smaller models, vote/average) — PoLL details not read here, only surveyed.

5. **Reference-answer comparison.** MT-Bench (S3): judges fail math even when they can solve the item **in a separate call** (misled by candidate answers). **Reference-guided**: generate the judge’s own answer first, then grade with that reference — failure on their 10-item math swap test **70% → 15%**. Prometheus 2 (S8) treats reference + custom rubric + verbal feedback as the standard input for both direct and pairwise grading.

6. **Checklist / narrative split; cheap+expensive.** DeepEval docs (S9, secondary) let you **skip auto-CoT** by supplying `evaluation_steps`, and recommend DAG metrics when you want deterministic yes/no graphs vs G-Eval’s non-determinism. No primary paper found that measures “Flash checklist then Pro narrative” for interviews. Closest cheap-control evidence: MT-Bench **few-shot judge** raises GPT-4 position consistency **65.0% → 77.5%** but authors say the longer prompts make API calls **4× more expensive** (S3); they default to zero-shot.

7. **Specialized evaluator models (distill).** Prometheus 2 (S8): open 7B / 8x7B judges, custom rubrics, optional reference. Pearson vs GPT-4-1106 on direct-assessment benches **~0.6–0.7** (README S10; paper Table 3 e.g. 7B vs GPT-4 on one bench 0.654). Pairwise human agreement claimed **72–85%** (S10). 7B “**16 GB VRAM**” (S10). Motivation is **affordability vs GPT-4 API**, not a second live grader. Infeasible on Render free 512MB.

### Agreement / bias — when extra judges help

- **Strong single judge + rubric already matches humans** at human–human levels (S3). Extra debate on GPT-4 is only **+2.5 pp** (S7).
- **Specialization helps most when the holistic prompt is weak or the model is small** (S4 MTS: huge QWK jumps for Llama-2; ChatGPT gains “moderate”). CodeEcho’s Gemini Pro + per-dimension evidence is closer to G-Eval/MTS *output shape* than to Vanilla holistic.
- **Orthogonal traits are complementary** (S4: 2 vs 4 traits). That argues for **distinct dimensions in one rubric**, not necessarily distinct API calls — MTS isolated traits to stop them contaminating each other.
- **Reference pass is the high-ROI second call** for technical/math items (S3 70→15), not a second persona.
- **Position swap is a 2× pairwise tax**; GPT-4 consistency only **65%** on near-duplicate answers (S3). Pointwise scorecards avoid this.
- **Biases (conflict across years):** 2023 MT-Bench: verbosity attack works; GPT-4 self-win **+10%**, Claude **+25%** (authors: cannot confirm self-enhancement). 2026 “Reliability without Validity” (S11): verbosity **<0.011** across 21 judges; kappa vs exact-match **deflates 33–41 pp**. 2026 “Judging the Judges” (S12): **style bias 0.76–0.92** dominates **position ≤0.04**; “combined budget” debias **+11.2 pp** on Claude Sonnet 4. Do not assume 2023 verbosity/position magnitudes still hold.
- G-Eval **prefers LLM-written summaries even when humans prefer human text** (S1 Fig. 2) — relevant if interview answers are compared to model keys.

### Cost multipliers vs one scorecard (~$0.02)

Relative **judge-call count** vs CodeEcho’s one Pro scoring call (token growth extra, unmarked):

| Pattern | Calls | ≈$/attempt | ≈attempts / $3 day | Evidence |
|---|---|---|---|---|
| Single structured scorecard | 1 | 0.02 | 150 | status quo |
| Same call + reference answer in prompt | 1 | ~0.02–0.03 | ~100–150 | S3, S8; token bump only |
| Independent solve, then reference-guided grade | 2 | 0.04 | 75 | S3 |
| Pairwise + conservative swap | 2 | 0.04 | 75 | S3 |
| Few-shot judge examples | 1 (4× tokens) | ~0.08 | ~37 | S3 “4× more expensive” |
| ChatEval default 2×2 (no extra swap) | 4 | 0.08 | 37 | S7 |
| ChatEval 2×2 + swap, or MTS 4 traits × 2 turns | 8 | 0.16 | 18 | S7, S4 |
| G-Eval n=20 logprob substitute | 20 | 0.40 | 7 | S1 |
| Debate 3 agents + summarizer | ≥9 | ≥0.18 | ≤16 | S7 |
| Prometheus 7B local | 0 API | VRAM | n/a on 512MB | S10 |

ChatEval/MTS also **serialize latency** (turns depend on prior text). A 4–8× stack leaves **~18–37 practice attempts/day** before STT/question-gen/other traffic — well below the 150 theoretical cap.

**Viable under free-tier ceiling:** keep one Pro scorecard; optionally **embed a model/reference answer** (1×); optionally a **gated second Pro call** only for technical/math or failed cheap checks. **[speculation]** A Flash yes/no checklist then Pro deep-pass is the usual product pattern but no primary interview paper priced it; Flash must be ≪ Pro or the gate does not pay. **Not viable as default:** debate/ensemble, per-trait sequential conversations, n=20 sampling, hosting Prometheus.

**Split graders (content vs delivery):** papers support *trait isolation* (S4, S5), not two hosted models. Cheapest isolation is **two sections in one JSON**. If split: put delivery/fluency on Flash and substance on Pro — **[speculation]** ~1.1–1.5× $ if Flash is ~5–20% of Pro, vs 2× for two Pro calls. Adversarial “does this actually answer the question” is a **reference-guided or checklist field**, not a third model.

Interview-product multi-model claims: **not established** from primary engineering writeups in this pass (see Conflicts).

## Conflicts and uncertainty

- 2023 position/verbosity magnitudes vs 2026 style-dominant / low-verbosity results (S3 vs S11/S12).
- ChatEval Table 1 absolute Acc. not extracted (only deltas + 62.5% at 3–4 roles).
- PoLL / PRE / PRD cost and agreement numbers not read (S2 survey only).
- No primary HireVue/interview-AI method for multi-grader cost; treat “5 models” marketing as untrusted.
- CodeEcho $0.02 and Gemini Flash/Pro ratio not re-verified this pass; table uses the brief’s $0.02 and linear call scaling **[speculation]**.
- Worker 01 owns dimension-count theory; MTS “4 traits better than 2” is noted only as a *call-count* implication.
- Worker 02 owns fluff signals; G-Eval LLM-preference bias is the only adjacent note.

## Quotes

- “GPT-4 judge match human evaluations at an agreement rate exceeding 80%” (S3)
- “few-shot judge… API calls 4× more expensive” (S3)
- “failure rate (from 70% to 15%)” after reference-guided math judge (S3)
- “improves the accuracy by 6.2% for ChatGPT and 2.5% for GPT-4” (S7)
- “same role prompt… cannot effectively enhance… compared with single-agent” (S7)
- “maximum gains of 0.437 on TOEFL11 and 0.355 on ASAP” (S4)
- “G-EVAL-4… Spearman correlation of 0.514 with human on summarization” (S1)
- “requires only 16 GB of VRAM” for Prometheus 2 7B (S10)

## Sources

id | url | title | published | tier | note
--- | --- | --- | --- | --- | ---
S1 | https://aclanthology.org/anthology-files/pdf/emnlp/2023.emnlp-main.153.pdf | G-EVAL: NLG Evaluation using GPT-4… | 2023-12 | primary | EMNLP 2023; also arXiv:2303.16634
S2 | https://arxiv.org/abs/2412.05579v2 | LLMs-as-Judges: A Comprehensive Survey | 2024-12 | primary | taxonomy; ChatEval/PoLL/PRE cited, not re-read
S3 | https://arxiv.org/html/2306.05685v4 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | 2023-06 | primary | NeurIPS 2023 PDF: https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and-Benchmarks.pdf
S4 | https://aclanthology.org/2024.findings-emnlp.10/ | Unleashing LLMs’ Proficiency in Zero-shot Essay Scoring (MTS) | 2024-11 | primary | Findings EMNLP 2024
S5 | https://aclanthology.org/2025.findings-naacl.322/ | Rationale Behind Essay Scores (RMTS) | 2025 | primary | Findings NAACL 2025; needs fine-tune
S6 | https://aclanthology.org/2025.findings-acl.1054/ | TRATES: Trait-Specific Rubric-Assisted AES | 2025 | primary | Findings ACL 2025; LLM features + regression
S7 | https://arxiv.org/pdf/2308.07201 | ChatEval: … Multi-Agent Debate | 2023-08 | primary | default 2×2; personas mandatory
S8 | https://arxiv.org/html/2405.01535v2 | Prometheus 2 | 2024-05 | primary | specialized open judge
S9 | https://deepeval.com/docs/metrics-llm-evals | DeepEval G-Eval docs | unknown | secondary | product docs; skip-CoT / DAG
S10 | https://github.com/prometheus-eval/prometheus-eval | prometheus-eval README | 2024-05 | primary | 16GB; 0.6–0.7 Pearson; 72–85% pairwise
S11 | https://arxiv.org/html/2606.19544v1 | Reliability without Validity | 2026-06 | primary | 21 judges; kappa deflation; low verbosity
S12 | https://arxiv.org/html/2604.23178 | Judging the Judges | 2026-04 | primary | style≫position; ensemble S3 not fully read
S13 | https://www.evidentlyai.com/llm-guide/llm-as-a-judge | Evidently LLM-as-a-judge guide | unknown | secondary | pairwise vs criteria vs reference; no cost study

## Needs-browser

(none)

## Searched

- LLM as judge survey
- G-Eval LLM judge
- MT-Bench Chatbot Arena judge
- ChatEval multi-agent debate
- LLM automated essay scoring traits
- Prometheus 2 LLM judge
