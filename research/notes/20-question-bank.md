# 20 — Curated vs LLM-generated interview question banks

**Worker:** research-worker · **Budget used:** 16/12 calls (cap 20) · **Date:** 2026-08-30 · **Scope:** quality, bias, repeatability, hybrid wins; seniority/bucket calibration; labeling offline/mock vs live gen. **Out of scope:** ingesting copyrighted banks; competitive pricing.

**Recommendation (evidence-weighted):** For a free demo, treat a **curated/offline mock bank as pretest-grade content** and **live LLM generation as uncalibrated drafts**. Hybrids win: blueprint/taxonomy + constrained gen + human or dual-LLM filter + IRT/field evidence before treating items as comparable. **Never silently swap** a static mock bank for live gen (or vice versa)—SIOP consistency/fairness and AIG “enemy item” literature both say different sources are different instruments.

## Findings

- **F1. Assessment literature treats banks and generation as different units of analysis.** Traditional development: SME writes, edits, reviews **one item at a time** (costly bottleneck). Template AIG (Gierl 3-step): SME builds a **cognitive model + item model**; algorithms permute constrained variants (e.g. one medical model → **528** items). Bank management must then track **models and items**, with a priori taxonomy codes—not ad hoc tags. Generated siblings are expected to be related; “enemy items” (cannot co-appear) and duplicates must be tracked. **S1, S2** primary.

- **F2. LLM-AIG literature is large on volume, thin on quality.** Tan et al. reviewed **60** LLM-AIG studies (IJATE 2025). LLMs generate many item types/languages/domains, but **many studies skip measurement properties** (difficulty, discrimination) and SME/measurement-specialist involvement; lots of NLP/AQG work stays at remember/understand, not apply/analyze. Authors: generation is not the end—evaluate with CTT/IRT + pedagogical fit. Isley et al. cite the same Tan gap. **S3** primary; **S4** corroborates.

- **F3. When hybrids are run like test development, SME preference can favor LLM drafts—review still required.** Pearson IJSA (2025), data-science **selection** MCQs: dual custom GPTs (writer + evaluator) + **RAG blueprint** (SME-reviewed 2nd/3rd-level topics) + I-O psychometric/fairness checklist. Blind paired comparison: SMEs preferred LLM items in **60%** of **n=205** pairs (z=2.86, p=0.002). Keep/revise vs drop **not** different by writer (GPT drop 32% vs human 36%). GPT drafts took **longer** to revise (M 3.78 vs 2.82 min; ~**+1 min**/item). Authors estimate **~70%** time savings on generation workflow vs recruiting/training writers—not a no-review pipeline. Failure modes: multiple keys, throwaway distractors. ChatGPT UI: **no temperature/top_p control** → **repeatability gap**; they recommend API. Domain split: Computational Foundations preference **23%** but **one SME** only. **S5** primary (vendor authors; method is empirical).

- **F4. Large classroom field study: after iterative gen–judge–refine, IRT looks comparable to a curated bank—but not interchangeable.** Isley et al. (arXiv 2025-08): o3-mini Self-Refine loop on instructor materials; AI-judge labels good/bad; final judge drops misfit/wrong-key; **hardest 10 of 20** kept because informal review found gen items **too easy**. 91 college classes, **1,686** students; **1,208** AI exams vs **478** AP-Stats-bank exams (stats courses only). Blind: neither students nor instructors told source. 2PL: AI mean difficulty **β̄=−0.45** (~60% correct) vs std **β̄=0.35** (~39% correct); Δβ posterior mean **−0.79**. Discrimination **ᾱ 1.3 vs 1.2** (Pr(δα>0)≈0.85). Test info Imax **3.85 vs 2.61** (R≈0.79 vs 0.72). Limits: assignment not randomized; AP comparison **stats-only**; MCQ only. **S4** primary, preprint.

- **F5. Operational AIG still filters hard: Duolingo IR retained 58% after human review, then fielded on a labeled practice test.** Attali et al. (Front. AI 2022): transformer AIG for DET interactive reading. **789→454 passages (58%)** after human review (~15 min/passage). Pilot on **DET practice test** (explicitly practice, not operational DET); **~200k** sessions; **5,246** items; mean item-total **0.27**; **6%** of items item-total <0.1. Local dependence risk **higher** because items are auto-generated from one passage. **S6** primary.

- **F6. Other published retain rates (cited, not re-run) are harsher than Pearson’s drop table.** Pearson discussion: Götz et al. ~**1/4** of AI personality items passed face-validity inspection; Hommel et al. ~**1/10** retained after duplicate/syntax/multidimensional culls. Attali 58% is passage-level after review. Treat “LLM items are good enough raw” as **false**. **S5** secondary for Götz/Hommel numbers; **S6** primary for 58%.

- **F7. Calibration of seniority/bucket is a blueprint + constraint problem, not a one-shot prompt.** What works in the papers: (1) **a priori taxonomy/blueprint** on models and items (Gierl ICD/SNOMED-style codes; Pearson expanded blueprint in RAG); (2) **template/cognitive-model constraints** so variants stay in-construct; (3) **AI-judge difficulty + correctness** then pick a target band (Isley: gen ran easy → take hardest decile); (4) **field IRT** before claiming a level (Isley, Attali); (5) **pretest then promote** only if stats pass (S8). Prompting “senior” without a rubric is the failure mode Tan flags (no defined construct). For CodeEcho: tag bucket/seniority on the **prompt spec and the stored item**, same as model-level content codes. **S1, S2, S3, S4, S5, S8**.

- **F8. Repeatability: live gen ≠ a banked form.** Same generating model → related items (Gierl enemy-item / exposure). Live ChatGPT-style gen without logged model, seed, and hyperparameters is **not reconstructible** (S5). SIOP: scores must be **consistent across replications**; **continually updating** algorithms means later candidates are not on the same standard—document version and when change is allowed. **S1, S5, S7**.

- **F9. Bias: training-data + construct contamination, not just “mean differences.”** Kaldaras et al. (Front. Educ. 2024): GAI tools inherit **social biases** in training data; if GAI invents “typical student” answers, it may propose **lower-proficiency / inaccurate** responses for some demographic prompts; also misses non-standard correct language. SIOP (Jan 2023): AI hiring tools need **same** validity/reliability/fairness bar as traditional tests; training-sample bias propagates; measurement bias = **job-irrelevant** variance by group; fairness includes **equitable access to practice materials**. Pearson applied Flesch–Kincaid ≤14 and a fairness checklist. No first-party study found that **SWE interview stems** are DIF-clean when LLM-generated. **S7, S9, S5**.

- **F10. How to label mock/offline vs live gen (demo-relevant).** High-stakes **pretest items** are usually **unlabeled** and **unscored**, embedded so candidates try equally; only items with good stats are **promoted to operational/scored** (S8 cites AERA/APA/NCME 2014; up to **~20%** of form length). That is the **opposite** of a product honesty problem. Attali fielded AIG on a **named practice test**, not as silent operational DET. SIOP: tell candidates what data/process is used; document algorithm version. Isley hid AI vs AP **for research blinding**, not as a product pattern. **For CodeEcho:** label **“static mock bank — not this session’s generator”** vs **“generated this session — uncalibrated / not banked”**; do not mix scores. Optional: “pretest” analog = collect stats before promoting a generated item into the offline bank. **S6, S7, S8**.

- **F11. Interview platforms (first-party, [marketing]): they sell hybrids, not raw live-gen banks.** **interviewing.io** homepage: AI Interviewer is FAANG-style coding/SD with feedback on **200+ problems from Beyond Cracking the Coding Interview** (curated book bank); human interviewers are Senior/Staff/Principal who “design” questions. **Hello Interview**: Premium = written breakdowns + **Guided Practice** on a **fixed** set (34 SD problems named on practice page; LLD/AI-coding/behavioral tracks) with **AI feedback** “tuned by FAANG interviewers”; separately a **reported** question library (**5.2k** on premium page vs **12,000+** on practice/pricing copy—see conflicts). Behavioral: “every role & level.” Neither page claims unconstrained live generation is the scored item source. **S10, S11, S12** [marketing].

- **F12. When hybrids win (synthesis for a free LLM budget).** Winner pattern across S3–S6: **small curated stems / models** (cheap, repeatable, seniority-tagged) + **LLM for variants, follow-ups, or first drafts** + **filter** (second model or cheap human) + **do not score live-gen like banked items**. Template/RAG beats zero-shot (S5, S3). Dual-LLM + SME beats LLM-alone (S5; Götz/Hommel retain rates). Offline mock bank is the right place to spend rare SME time; live gen is for coverage/freshness if labeled. Cutting a curated bank for deadline is a known quality/repeatability risk (F2, F8), not just a content-gap risk.

## Conflicts and uncertainty

- **SME preference vs IRT vs retain rate:** S5 SMEs like LLM MCQs 60% after heavy process; S4 AI items easier than AP bank; S6 keeps only 58% of AIG passages; Götz/Hommel (via S5) keep 10–25%. Not the same construct or stake. Do not collapse to “LLM ≥ human.”
- **Hello Interview library size:** S11 **5.2k** “Reported Interview Questions” vs S12 **12,000+** library. Unresolved; both [marketing].
- **SIOP S7** is about **hiring assessments**, not candidate-prep products. Transfer: documentation, consistency, and “tell the user what instrument this is.” Not a legal mandate for a demo.
- **No first-party SWE study** of generated vs curated **behavioral** stems with IRT or inter-rater difficulty. Extrapolation from MCQ/classroom/English-test AIG.
- **Seniority calibration:** platforms claim level filters [marketing]; psychometrics only show **difficulty controls** (blueprint, AI-judge, IRT)—not a validated “E5 vs E3” generator.
- **S4** preprint, 0 citations at fetch; AP arm not randomized. **S5** Pearson authors evaluating their own pipeline.
- **Pretest unlabeled (S8)** vs **product should label (F10):** conflict is **purpose** (score integrity vs user honesty), not a single rule.
- Worker 14 owns pricing; IGotAnOffer/johal numbers unused.

## Quotes

- S1: "With AIG, items are managed at the model level."
- S1: "generated items may be more closely related to one another"
- S3: "many studies have overlooked the quality of the generated items"
- S3: "evaluating both the measurement properties and pedagogical soundness"
- S4: "AI-generated questions performed comparably to expert-created questions"
- S4: "somewhat easier but also more discriminating than the expert-produced questions"
- S5: "SMEs selected LLM-generated items in 60% of the comparisons"
- S5: "human review of LLM-developed items was critical"
- S6: "a final set of 454 out of 789 passages (58%) were retained"
- S7: "same level of scrutiny and should meet the same standards"
- S7: "algorithms that are being constantly updated" / "not competing … on the same standards"
- S8: "Pilot questions … do not count towards candidate’s scores"
- S10: "work over 200 problems from Beyond Cracking the Coding Interview"
- S12: "step-by-step AI interviewer" on "real interview questions"

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2022.853578/full | Gierl et al. Content coding + AIG security | 2022-05-04 | primary | Frontiers; model vs item banking |
| S2 | https://www.scitepress.org/Papers/2025/134910/134910.pdf | Firoozi & Gierl banking strategies | 2025 | primary | CSEDU; a priori vs posthoc codes |
| S3 | https://dergipark.org.tr/en/pub/ijate/article/1602294 | Tan et al. LLM AIG review (60 studies) | 2025 | primary | IJATE 12(2) 317–340; PDF also fetched |
| S4 | https://arxiv.org/abs/2508.08314 | Isley et al. AI-generated exams field study | 2025-08-09 | primary | preprint; IRT 2PL; Harvard/Microsoft fund |
| S5 | https://doi.org/10.1111/ijsa.70021 | Kowal et al. AI vs human items | 2025-08-01 | primary | IJSA; Pearson authors [marketing-adjacent] |
| S6 | https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2022.903077/full | Attali et al. DET interactive reading AIG | 2022-07-22 | primary | Duolingo; 58% retain; practice-test pilot |
| S7 | https://www.siop.org/wp-content/uploads/2024/06/Considerations-and-Recommendations-for-the-Validation-and-Use-of-AI-Based-Assessments-for-Employee-Selection-January-2023.pdf | SIOP AI-based assessments | 2023-01 | primary | Hiring focus; Principles-aligned |
| S8 | https://www.proftesting.com/blog/2017/03/22/pretest-questions-use/ | Professional Testing pretest explainer | 2017-03-22 | secondary | Vendor blog; cites 2014 Standards |
| S9 | https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1399377/full | Kaldaras et al. valid assessments + GAI | 2024-08-07 | primary | Conceptual; AERA Standards framing |
| S10 | https://interviewing.io/ | interviewing.io homepage | unknown | low | [marketing] AI Interviewer + BCTCI bank |
| S11 | https://www.hellointerview.com/premium | Hello Interview Premium | unknown | low | [marketing] 5.2k reported Qs |
| S12 | https://www.hellointerview.com/practice | Hello Interview Guided Practice | unknown | low | [marketing] fixed problem tracks + AI |

## Needs-browser

- https://www.siop.org/post/siop-releases-recommendations-for-ai-based-assessments/ — fetch.py exit 4 (HTTP 403); PDF S7 already read
- https://interviewing.io/ai — fetch.py exit 4 (HTTP 404); homepage S10 used instead

## Searched

item bank vs generative items, automated item generation IRT, interviewing.io question bank, Hello Interview question bank, SIOP AI assessment item validation, pretest items vs operational labeling, interviewing.io AI Interviewer problems, Tan Armoush LLM item generation review, Hello Interview recent interview questions
