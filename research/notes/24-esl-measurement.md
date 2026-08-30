# Note — Measuring ESL / delivery-metric bias (audit methods)

**Worker:** 24 · **Budget used:** 18/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** Concrete methods to measure accent/L2 disparity on pipelines that score fillers, WPM, pauses (CodeEcho-like). What to log; how to interpret subgroup gaps; one-time audit without collecting protected-class labels at scale. Out of scope: competitor UI, threat model, analytics product, design spec, CodeEcho code. Complements note 21 (mitigations); this note is measurement only.

**Recommendation (evidence-weighted):** Do not collect production-user race/L1/accent labels. Run a **one-time offline audit** of the production ASR + filler/WPM/pause heuristics on **public labeled eval sets** (Fair-Speech, Artie Bias, L2-ARCTIC). Report **three layers**: (A) ASR WER vs gold, (B) delivery features on **gold** transcripts, (C) delivery features on **ASR hypotheses**. Interpret with **speaker-averaged** rates + **mixed-effects Poisson** (Liu et al. 2022) and 95% CI on group ratios — not raw mean WER. A WER gap that vanishes on gold → ASR contamination. A pause/WPM gap that remains on gold → construct (L2 encoding), not “detector bias,” unless the construct is defined as nativeness (note 21). Optional unlabeled production check: confidence / challenging-subgroup models (Koudounas et al. 2025) or utterance clustering (Dheram 2022 / Veliche & Fung 2023) — never train a demographic predictor (Fair-Speech DUA).

## Findings

- **F1. No NIST speech-fairness standard; process standards exist.** NIST OpenASR is a **low-resource-language** ASR challenge, not accent/L2 fairness. What exists: NIST AI RMF **MEASURE 2.11** — “Fairness and bias… are evaluated and results are documented”; playbook asks for acceptable error **distributions**, TEVV, and documenting unmeasured risks. IEEE **7003-2024** (published 2025-01-24): validation-set selection for bias QC, **application boundaries**, user-expectation management (correlation vs causation). IEEE **3198-2025** (published 2025-05-26): fairness definitions, metrics, and test-case procedures — **PDF unread** (paywalled). SpeechBrain documents WER/CER/EER only; **no fairness audit API**. **S1–S5**.

- **F2. Current ASR fairness *measurement* stack = labeled eval set + mixed-effects Poisson.** Liu, Veliche & Peng (ICASSP 2022 / arXiv 2109.09061): do **not** compare subgroup WER means. Model utterance error **counts** as Poisson with `log(N_words)` offset, **speaker random effect**, subgroup + confounders as fixed effects; LRT for the factor; avoids underestimated SEs and false-positive “unfair.” Add sentence embeddings as covariates: if the group effect **survives**, residual gap is acoustic/prosodic, not lexical. Fair-Speech (Veliche et al., Interspeech 2024): 26,471 utts / 593 US speakers; self-report L1 vs L2 (482 / 111 speakers; 21,528 / 4,943 utts); gold annotation WER **1.47%**; DUA **forbids training models that predict those labels**. They apply Liu’s model + bootstrap **95% CI on WER ratio**; CI excluding 1 = significant. ASR-FAIRBENCH (Interspeech 2025) wraps the same Poisson + WER into FAAS and five-tier labels — **leaderboard, not a product spec**. **S6–S8**.

- **F3. How to interpret a subgroup gap (do this before claiming “bias”).** Herron et al. (2026, arXiv 2605.10615) best-practice belt, after reading Fair-Speech: (1) **speaker-average** WER, not utterance-pool (independence + speaker imbalance); (2) ~**35 speakers/SG** for a one-sided two-sample Z at 95%/power 0.8 if δ̂=0.1, σ=0.15 — more utterances **cannot** shrink speaker variance below σ; (3) **condition** on other DVs / intersectionality or raw gaps are dataset artifacts; (4) control **SNR** and **text complexity** (Koenecke-style perplexity / dialect density) if the question is acoustic; (5) drop z>3 speaker outliers on small SGs; (6) middle-age WER splits with no phonetic reason = **balancing failure**. Fair-Speech raw Whisper L2 WER **lower** than L1 (rel. gap 41–47%) — **opposite** most L2 studies; Herron shows this is largely **Black L1 English**, not “L2 is easier.” **S7, S9**. Transfer: a CodeEcho Delivery gap that is only L1 vs L2 **unadjusted** is not evidence.

- **F4. Public test sets that avoid collecting *your* users’ protected-class labels.** Fair-Speech (eval-only, consenting paid speakers). Artie Bias Corpus (Meyer et al., LREC 2020): 1,712 CC0 Common Voice clips with opt-in age/gender/accent; ships `detect_bias.py` (WER or **CER** + ANOVA on group CER); DeepSpeech baseline Indian vs US CER **40.50% vs 21.50%** (p=8.54e−32), gender n.s. (p=0.061). L2-ARCTIC (Zhao 2018; used throughout later work): 24 L2 speakers, six L1s (AR, ZH, HI, KO, ES, VI) + L1-ARCTIC control; **read** speech — good for ASR robustness, **bad** for spontaneous pause/filler construct. AequeVox used Speech Accent Archive + Nigerian/Midlands sets. Casual Conversations / CORAAL / Voices of California are the Koenecke-class interview sets (racial, not L2). **S7, S10, S11**.

- **F5. Filler-word detectors: published failure modes are phonetic confusion and ASR coupling — not L2-stratified F1.** PodcastFillers (Zhu, Cáceres & Salamon, 2022): 35k fillers / 145 h / 350+ speakers. ASR typically **omits** uh/um; candidates = VAD-on ∩ ASR-off. AVC (ASR+VAD+classifier) >> transcription-free VC; VC false-positives on words that sound like fillers (Das et al.: “umbrella”). Zhu follow-on (arXiv 2303.06475): top FPs **a, the, uh-huh, oh, I**; missed **uh** after *and/but/the*; **200 ms** alignment slack causes FP+FN. **No paper fetched reports filler F1 by L2/accent.** Implication: a heuristic that counts ASR tokens `uh/um` inherits **both** ASR omission (under-count) and substitution of schwa-like function words (over-count). Layer C vs B (F8) is the measurement. **S12, S13**.

- **F6. WPM / speaking-rate: ASR error rises at extreme ROS; high rate is a “challenging subgroup” feature, not a fairness label.** Zhu et al. (2015, arXiv 1506.00799): “significant performance reduction” when rate of speech is too low or too high; ROS changes **static and dynamic** acoustics. Koudounas et al. (ACL 2025 Industry): DivExplorer challenging subgroups on FSC include `{age=41-65, gender=male, speakRate=high}` and high `totSilence` — **speaking rate and pause totals are first-class metadata** for disparity mining. Confidence-model features explicitly include **word count, pauses, speaking rate, SNR**. This is the closest published logging schema to CodeEcho Delivery. A gold-transcript WPM gap for L2 is the SLA construct in note 21, not proof the meter is biased. **S14, S15**.

- **F7. Audits without protected-class labels at *runtime*.** (a) **Offline public sets (F4)** — preferred one-time check. (b) **CSI / confidence model** (Koudounas et al. 2025, Amazon+PoliTo): train on a **held-out labeled** set once; at runtime predict “challenging” from uncertainty, embeddings, and speech metadata — **no age/gender/accent collected in production**. Metadata-oracle is only slightly better. (c) **Unsupervised utterance clustering** (Dheram et al. Interspeech 2022; Veliche & Fung ICASSP 2023): cluster acoustics, acquire/score hard clusters; Meta blog: geographic/ethnicity labels are **poor accent proxies**. (d) **AequeVox** (Rajan et al. 2021): two ASRs, no gold; fairness = unequal **degradation** under noise/filter transforms vs a base group; Speech Accent Archive **native vs non-native**: non-native generated **109% more errors** on average than native across Google/Azure/IBM. Still needs a **group-labeled public set**, not production users. (e) **Do not** train demographic classifiers (Fair-Speech DUA; Herron notes some jurisdictions forbid ethnic-minority analysis). **S7, S15–S17**.

- **F8. Minimal schema + protocol for a small free-tier product.** **One-time offline (no user PII):** run pipeline on Fair-Speech + Artie + (optional) L2-ARCTIC. Per utterance log: `utt_id`, `speaker_id`, `duration_s`, `n_words_asr`, `n_words_gold` (if any), `wer`, `ins/del/sub`, `wpm_asr`, `wpm_gold`, `filler_n_asr`, `filler_n_gold`, `pause_n`, `mid_unit_pause_n` (threshold logged), `snr_db`, `asr_conf` or n-best length, `asr_vendor/model`. Aggregate **per speaker** then SG. Fit Liu Poisson on error **counts** and, analogously, on filler/pause **counts** with `log(n_words)` offset. **Three-layer read:** A WER(L2)>WER(L1) → Delivery on ASR is contaminated; B gold WPM/pause L2≠L1 → expected fluency construct (disclose, don’t “fix” by equalizing); C ASR-minus-gold filler Δ larger for L2 → **measurement bias** to ship a disclosure + transcript edit (note 21). **Unlabeled production (optional, later):** same numeric fields **without** SG labels; flag high-error / low-conf / CSI-positive share; do not infer ethnicity. IEEE 7003: write a **bias profile** + “Delivery is not an accent or hireability score” boundary. **S1, S6, S9, S15**.

## Conflicts and uncertainty

- **L1 vs L2 WER direction:** Fair-Speech Whisper: L2 **better** than L1 (raw). Most cited studies (Feng, Ghorbani, Zhang/Scharenborg, AequeVox) find L2/non-native **worse**. Herron: Fair-Speech L1 pool is ethnicity-confounded. Do not quote a universal L2 WER multiplier.
- **Gender:** Veliche et al. report large male>female WER; Herron says it shrinks after intersectional conditioning. Same dataset, different method.
- **IEEE 3198-2025** metric formulas unread (subscription). Do not invent IEEE metric names.
- **No published filler-F1 × L2 table.** F5 is mechanism (ASR coupling + phonetic FP), not a measured L2 gap.
- **L2-ARCTIC is read speech** — pause/filler rates are not interview-valid.
- **SpeechBrain / HuggingFace:** no first-party speech-fairness cookbook found; WER subgrouping is DIY.
- **Google first-party speech fairness report:** not found this pass. AequeVox is third-party on Google/Azure/IBM.
- **ASR-FAIRBENCH FAAS formula** taken from paper abstract/body via search extract; PDF not fetch.py’d — treat FAAS tiers as [unconfirmed] if unused.
- **Out of scope parked:** UGESP/SIOP (note 21); live competitor UI (23).

## Quotes

- S1: "Fairness and bias – as identified in the MAP function – are evaluated and results are documented."
- S2: "criteria for the selection of validation data sets for bias quality control"
- S6: "prevents underestimating the standard errors and avoids drawing false positive conclusions"
- S7: "data user agreement prevents a user from developing models that predicts the value of those labels"
- S9: "we would need n≈ 35 speakers per SG"
- S12: "leveraging ASR strongly outperforms a keyword spotting approach"
- S15: "without the need to access or collect sensitive information"
- S16: "non-native English, female and Nigerian English speakers generate 109%, 528.5% and 156.9% more errors"

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://airc.nist.gov/airmf-resources/playbook/measure/ | NIST AI RMF Playbook — Measure | unknown / live 2026-08 | primary | MEASURE 2.11; error distributions; TEVV |
| S2 | https://standards.ieee.org/ieee/7003/11357/ | IEEE 7003-2024 Algorithmic Bias Considerations | 2025-01-24 | primary | Abstract+scope only; full PDF unread |
| S3 | https://standards.ieee.org/ieee/3198/11068/ | IEEE 3198-2025 ML Fairness Evaluation | 2025-05-26 | primary | Abstract only; metrics unread |
| S4 | https://www.nist.gov/itl/iad/mltg/openasr-challenge | NIST OpenASR Challenge | 2020–2021 | primary | Low-resource langs; not accent fairness |
| S5 | https://speechbrain.readthedocs.io/en/stable/API/speechbrain.utils.metric_stats.html | SpeechBrain metric_stats | unknown | primary | WER/CER/EER; no fairness module |
| S6 | https://arxiv.org/html/2109.09061 | Model-based ASR fairness — Liu et al. | 2021-09-19 | primary | Mixed-effects Poisson; ICASSP 2022 |
| S7 | https://arxiv.org/html/2408.12734 | Fair-Speech dataset — Veliche et al. | 2024-08-22 | primary | Interspeech 2024; L1/L2 counts; DUA |
| S8 | https://arxiv.org/pdf/2505.11572 | ASR-FAIRBENCH — Rai et al. | 2025 | primary | FAAS; Fair-Speech 10% sample [partial read] |
| S9 | https://arxiv.org/html/2605.10615 | Responsible benchmarking ASR fairness — Herron et al. | 2026-05-11 | primary | Speaker-avg; n≈35; Fair-Speech pitfalls |
| S10 | https://aclanthology.org/2020.lrec-1.796/ | Artie Bias Corpus — Meyer et al. | 2020-05 | primary | PDF via reader; CER+ANOVA; detect_bias.py |
| S11 | https://aclanthology.org/2021.icnlsp-1.2.pdf | ASR for L2 English — (L2-ARCTIC use) | 2021 | secondary | Establishes L2-ARCTIC as L2 WER bench |
| S12 | https://arxiv.org/abs/2203.15135 | PodcastFillers — Zhu et al. | 2022-03-28 | primary | AVC vs VC; ASR-off filler candidates |
| S13 | https://arxiv.org/pdf/2303.06475 | Transcription-free fillers — Zhu et al. | 2023-03 | primary | FP list a/the/I; 200 ms slack |
| S14 | https://arxiv.org/abs/1506.00799 | Learning speech rate in ASR — Zhu et al. | 2015-06 | primary | Extreme ROS hurts WER |
| S15 | https://aclanthology.org/2025.acl-industry.52.pdf | Privacy-preserving CSI — Koudounas et al. | 2025-07 | primary | ACL Industry; Amazon; log pauses/WPM |
| S16 | https://arxiv.org/abs/2110.09843 | AequeVox — Rajan et al. | 2021-10-19 | primary | Diff test; +109% non-native errors |
| S17 | https://www.isca-archive.org/interspeech_2022/dheram22_interspeech.pdf | Toward fairness in ASR — Dheram et al. | 2022 | secondary | Clustering cited via S15/S9; PDF unread this pass |

## Needs-browser

- https://aclanthology.org/2020.lrec-1.796.pdf — fetch.py exit 3 (PDF). Body used from rendered extract (S10).
- https://standards.ieee.org IEEE Get Program PDFs for 7003/3198 — HTML abstracts only (S2, S3).
- https://ai.meta.com/datasets/speech-fairness-dataset/ — fetch.py HTTP 400. Paper HTML used (S7).
- https://www.isca-archive.org/interspeech_2025/rai25_interspeech.pdf — ASR-FAIRBENCH ISCA PDF not fetch.py’d (S8 via arXiv).
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf — RMF PDF available; Measure HTML sufficient (S1).
- HuggingFace `evaluate` fairness speech page — not found as a first-party speech cookbook.

## Searched

- NIST ASR fairness audit
- IEEE speech bias standard
- SpeechBrain fairness evaluation
- HuggingFace speech fairness
- filler word detection bias
- L2 fluency metric audit
- proxy fairness without demographics
- Fair-Speech dataset Meta ASR
- fairness without demographics speech
- Google ASR fairness report
- AequeVox ASR differential testing
- L2-ARCTIC ASR WER evaluation
- Don't speak too fast speech rate ASR
- Artie Bias Corpus Common Voice
- Liu Veliche Peng fairness ASR Poisson
