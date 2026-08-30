# Note — Rubric dimensions (count, granularity, reliability)

**Worker:** 01 · **Date:** 2026-08-30 · **Scope:** SWE/behavioral interview rubric dimension counts; LLM-as-judge multi-criteria evidence; spoken-answer axes vs deepening.

**Recommendation (evidence-weighted):** **Keep (~7–8) or redesign down to 3–5 orthogonal competencies. Do not expand to 9 named sections.** Adding axes fights first-party SWE scorecards (3–4), STAR’s 4-part *time* split, and LLM-judge results that more co-present criteria increase halo/interference and tokens.

## Findings

- **F1. interviewing.io: 3 axes + hire/no (not ~9).** Form: advance yes/no; Technical (Code), Problem-solving (Solve), Communication (Communicate), each 1–4. On 100K interviews, a −1 on Code/Solve can raise rejection ~6× in a large slice; Communicate is the weakest +1/−1. Coding-only caveat: behavioral → “problem solving is king”; systems design → extra Communicate still least of three. L3–L4: ignore Communicate if consistently ≥2. **S1** primary (platform data; guest author).

- **F2. Google re:Work (Mar 2026): 3 hiring-attribute categories.** RRK, Problem solving, Leadership. Anchors: poor / borderline / solid / outstanding. Structured interviews + BARS-style rubrics claimed more predictive than unstructured; ~40 min saved per interview; rejected structured candidates 35% happier. Live page does **not** list Googleyness or a 1–4 bar. **S2** primary.

- **F3. Amazon official: 16 Leadership Principles as culture, not a per-answer 9-box scorecard.** **S3** lists 16 LPs; no public 1–5 scale or “score N sections per story.” Prep-site claims (2–4 LPs/interviewer, 1–5 hire) are unread first-party → [unconfirmed]. 16 LPs are *loop coverage*, not a reason to add 2 boxes on one spoken answer.

- **F4. Hello Interview SD rubric: 4 competencies.** Problem Navigation, Solution Design, Technical Excellence, Communication and Collaboration. Company wording differs; themes shared. Meta E5 coding (same site): Problem Solving, Code Quality, Verification, Communication — again **4**. **S4, S8** secondary [marketing].

- **F5. MIT CAPD STAR: 4 elements as *time* allocation, not 8 scored dimensions.** Situation 20%, Task 10%, Action 60%, Result 10% — “time to dedicate”; “most of your response should focus on your Actions.” Coaching to *deepen Action*, not add letters. **S7** primary (university career office).

- **F6. G-Eval (Liu et al. 2023): 4 SummEval aspects; prompt rates “one metric.”** Table 1: Coherence, Consistency, Fluency, Relevance (1–5). Prompt: “rate the summary on one metric.” CoT helps; G-Eval-4 AVG Spearman ρ 0.514 vs human. Authors: judges are “sensitive to the instructions and prompts.” GPT-4 used n=20 samples to estimate scores (cost-heavy). **S5** primary. Not an interview rubric; closest cited multi-criteria LLM-judge method.

- **F7. ComplexEval (Li et al., arXiv 2509.03419 / Findings EMNLP 2025): more rubric dimensions buy granularity and also halo + attention limits.** Five biases include **Criteria Entanglement** (“halo effect”: similar scores across dimensions even when some are weaker) and **Criteria Loophole** (unlisted features get ignored). “While rubrics enable finer-grained assessment, their multi-dimensional complexity introduces new challenges.” Entanglement strong on holistic multi-dim writing rubrics; reduced when dimensions are scored independently (role-play), at “extra assessment overhead.” Multi-dim judging hits a **hard ceiling (~15 issues)** even as true issues rise; per-dimension calls lift the ceiling but add a 1–2 false-positive floor. Bias severity scales with task complexity; reasoning models more vulnerable. Rubrics/refs can raise clean accuracy (e.g. DeepSeek-v3 +4.74% with refs) and *hurt* under attack (−1.66%). **S6** primary.

- **F8. SARA (Yao et al., arXiv 2608.14684): joint multi-rubric scoring is cheaper and systematically inconsistent.** Isolation = one rubric per call; joint = all rubrics one pass. Joint introduces **rubric interference** (verdict on rubric *i* depends on co-present rubrics; even reorder can flip). Preliminary: only **one-third** of samples fully consistent across rubric-set compositions. Isolation vs joint on HealthBench: Qwen3-32B **36%** sample exact-match. HealthBench: **2–32 rubrics/sample, avg 11.5** (“most demanding”); FLASK: **3 fixed** 1–5 skills — “only 3 fixed rubrics limit the surface area for interference,” yet interference still measurable (Qwen3-32B EM .41→.59 after SARA). ResearchQA avg **7.5** (range 1–8). They **cap rubrics at 10/sample** in eval. Mitigation (SARA distillation) needs extra training — not a free-tier prompt tweak. **S9** primary, very new (2026-08) [unconfirmed] replication.

- **F9. Spoken-answer implication.** Public SWE/behavioral scorecards keep Communication as **one** of 3–4 competencies, not Delivery+Conciseness+…. MIT: deepen Action (substance). interviewing.io: extra Communicate points are the worst trade vs Solve/Code; behavioral value sits in problem-solving. LLM-judge: deepen via **clearer anchors / CoT / isolation of existing axes**, not more named boxes. Adding 2 sections toward 9 increases joint-prompt tokens and interference surface (S5, S6, S9) under a ~$3/day budget.

- **F10. CodeEcho today already at or above industry per-answer count.** Experience/STAR ~8 (S/T/A/R + Relevance, Specificity, Conciseness, Delivery); other modes ~7; coding ~5. Going to 9 moves *away* from 3–4 competency scorecards and into HealthBench-like high-N interference (S9) without a first-party interview precedent for 9 sections per answer.

## Conflicts and uncertainty

- **Google 3 vs 4 attributes:** S2 live re:Work = RRK, Problem solving, Leadership. Prep blogs claim fourth “Googleyness” + 1–4 scale / ~3.5 bar. Those numbers are **not** on fetched re:Work. Treat as [unconfirmed] secondary.
- **Amazon interview scoring protocol** is not on S3. 16 LPs ≠ 16 scores per answer.
- **No first-party Meta scorecard.** S8 is Hello Interview’s reconstruction [marketing].
- **No paper says “8 beats 9” on interview answers.** Extrapolation: industry 3–4; LLM interference rises with co-present N (S6, S9); HealthBench avg 11.5 is the stress case, FLASK’s 3 is the low-interference case. 7–8 already nearer ResearchQA’s 7.5 than FLASK’s 3.
- **SARA S9** is August 2026 arXiv; single-lab; [unconfirmed].
- **G-Eval** is summarization/dialogue, not spoken interviews. Transfer is analogical.
- **Worker 03 owns** ensemble/cost math; do not treat SARA isolation (N calls) as a recommended architecture here — only as evidence that joint 9-way scoring is the unreliable cheap path.
- SEO STAR “Action = 40–60% of *score*” pages unread / [marketing]; MIT S7 is time, not score weights.

## Quotes

- S1: "three other questions, each graded on a scale from 1 to 4 (4 is best)"
- S1: "In behavioral interviews, the technical skill signal is the least valuable, while problem solving is king."
- S2: "Here are three categories we find helpful."
- S2: "poor, borderline, solid, and outstanding answer"
- S4: "Problem Navigation, Solution Design, Technical Excellence, and Communication and Collaboration."
- S5: "Your task is to rate the summary on one metric."
- S6: "judges tend to assign similar scores across dimensions (a \"halo effect\")"
- S6: "multi-dimensional complexity introduces new challenges."
- S6: "Dimension-independent evaluation can ease such biases but adds extra assessment overhead."
- S7: "most of your response should focus on your Actions."
- S9: "only one-third of samples receive fully consistent verdicts"
- S9: "even Qwen3-32B achieves only 36%" (HealthBench isolation vs joint)
- S9: "only 3 fixed rubrics limit the surface area for interference"

## Sources

id | url | title | published | tier | note
---|---|---|---|---|---
S1 | https://interviewing.io/blog/does-communication-matter-in-technical-interviewing-we-looked-at-100k-interviews-to-find-out | Communication vs Code/Solve (100K interviews) | unknown | primary | Guest author; platform form + data
S2 | https://rework.withgoogle.com/intl/en/guides/a-guide-to-structured-interviewing-for-better-hiring-practices | Structured interviewing — Google re:Work | 2026-03 (page Updated March 2026) | primary | 3 attributes; 4 rubric anchors
S3 | https://www.aboutamazon.com/about-us/leadership-principles | Amazon Leadership Principles | unknown | primary | 16 LPs; no scoring protocol
S4 | https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction | System Design in a Hurry — Introduction | unknown | secondary | [marketing] 4-theme rubric
S5 | https://ar5iv.labs.arxiv.org/html/2303.16634 | G-Eval (Liu et al.) | 2023-05-23 (arXiv v3) | primary | 4 SummEval dims; one-metric prompt
S6 | https://arxiv.org/html/2509.03419 | Curse of Knowledge / ComplexEval (Li et al.) | 2025 (EMNLP Findings Nov 2025) | primary | Entanglement, loophole, attention ceiling
S7 | https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/ | MIT CAPD STAR method | 2022-06-13 | primary | 4 parts as time %, Action 60%
S8 | https://www.hellointerview.com/guides/meta/e5 | Meta E5 Interview Guide | unknown | secondary | [marketing] 4 coding aspects
S9 | https://arxiv.org/html/2608.14684 | Mitigating Rubric Interference / SARA (Yao et al.) | unknown (arXiv 2608.14684) | primary | Joint vs isolation; [unconfirmed] 2026

## Needs-browser

- Anthology PDF https://aclanthology.org/2025.findings-emnlp.805.pdf — fetch.py exit 3 (not HTML). Superseded by S6 arXiv HTML (exit 0). No remaining blocker.

## Searched

- Google interview scoring rubric
- Amazon leadership principles scoring
- interviewing.io interview rubric
- G-Eval multi criteria evaluation
- Google reWork hiring attributes
- Hello Interview scoring rubric
- LLM judge halo effect criteria
- STAR method four elements scoring
- ComplexEval Bench LLM judge
