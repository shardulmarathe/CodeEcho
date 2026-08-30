# Note — ESL / delivery-metric bias (filler, WPM, pauses vs content)

**Worker:** 21 · **Budget used:** 15/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** Bias when interview-prep tools score delivery (filler, WPM, pauses) and LLM content on L2/ESL speakers; free mitigations and disclosures. Recruiter-facing but fairness for users. Out of scope: i18n UI; non-English product.

**Recommendation (evidence-weighted):** Keep **Delivery** and **Content** as separate objects; never fold WPM/filler/pause into an overall “quality” or hireability number. Label Delivery as **pace/fluency signals, not accent or English quality**. Do not use native WPM bands as pass/fail. If a pause metric is shown, prefer **mid-clause / mid-unit** rate over raw pause count. Disclose that ASR can mis-hear accented speech and inflate fillers/WPM error. Lead recruiter-facing cards with content. Free: copy + split scores + transcript edit + no nativeness acoustic score.

## Findings

- **F1. Accent ≠ intelligibility; nativeness is the wrong target.** Munro & Derwing (1995): listeners often rated speech heavily accented while transcriptions stayed highly intelligible; “a strong foreign accent does not necessarily reduce” comprehensibility or intelligibility. Munro (2016): partial independence of accentedness vs intelligibility is “one of the most robust findings” in L2 pronunciation; adult L2 speech is typically non-native regardless of other proficiency; no reliable instruction produces native-sounding speech; goal is intelligibility, not accent elimination (Abercrombie 1949 via Munro). **S1** primary (abstract + methods summary), **S2** primary. Product: never imply a Delivery ding means “fix your accent.”

- **F2. L2 utterance fluency is not native WPM.** Gao, Sun & Li (2025, *Language Testing*): silent-pause **location** (mid- vs end-ASU) is construct-relevant; L2 studies commonly treat silent pauses as >250 ms (De Jong & Bosker 2013); Gao finds **200 ms** best predicts proficiency/perceived fluency in monologue, **200 ms** (proficiency) / **350 ms** (perceived fluency) in dialogue. Mid-unit pauses track linguistic encoding load; boundary pauses track planning. **S3** primary. Kallio et al. (2022): L2 speakers pause more **within** utterances than L1; fluent L2 speakers pause at grammatical junctures, disfluent ones inside clauses/phrases; mid-phrase and after incomplete words hurt perceived fluency. **S4** primary. SpeechRater 5.0 (Chen et al., ETS RR-18-10, 2018): vs L1, L2 speakers have reduced lexical/syntactic automaticity and **more frequent within-clause pauses**; features include `wpsec` (words/sec), silence rate/duration, fillers (“uh/um”), `withinClauseSilMean`, `IPC`. They separate **Delivery** (fluency/pronunciation/prosody/rhythm) from **Language use** and note **content** is hard and was late to add. **S5** primary. Implication: a single WPM or raw pause count vs a native band punishes normal L2 encoding time.

- **F3. ASR errors are systematically worse on non-standard / L2 speech — and they poison delivery metrics.** Koenecke et al. (PNAS 2020): five commercial ASRs (Amazon, Apple, Google, IBM, Microsoft); matched interview snippets; mean WER **0.35** Black vs **0.19** White (~2×); gap remains on **identical** short phrases → **acoustic/prosodic**, not lexicon. They explicitly warn of harm when employers use ASR to “automatically evaluate candidate interviews.” **S6** primary. Prasad et al. (arXiv 2205.08014, 2022): literature WER “as much as 85% higher” on AAVE vs SAE (citing prior); speakers may “standardize” and slow down; wav2vec pre-training cut GMU L2 Accent WER **8.2 → 4.0**. **S7** primary [secondary on the 85%]. Chen/ETS: human agreement on nonnative spontaneous speech rarely >85%; ASR WER may **bottom out ~10–20%** vs **≤5%** native. Fillers and pause features are taken **from ASR output**. **S5**. npj Digital Medicine (2026): Whisper WER penalty vs native β=**11.0** pp (95% CI 1.0–21.0); WhisperX β=**3.4** (p=0.07); WhisperX+GPT-4o attenuates to **1.7** pp. Clinical, scripted, small-n. **S8** primary. Any filler/WPM computed on a dirty transcript will falsely flag L2 speakers.

- **F4. LLM/text graders can add small L1 DIF even after accent is stripped.** Kwako et al. (BEA 2023): ELPA21 speaking, AWS `en-US` transcripts → off-the-shelf BERT. Human scores already show **moderate L1 DIF** in grades 9–12 (z_abs=.196). BERT **increases** L1 DIF (Δz_abs=.025, CI [.011,.039]) — statistically real, practically tiny. Longer items have more DIF. Removing audio did **not** remove DIF: text-only scoring does not “fix” L1 bias (transcripts still differ by L1). AWS transcription itself was L1-uneven (Vietnamese 9–12; details in Kwako 2023, not this paper). **S9** primary. Wei et al. (arXiv 2608.06300, 2026): fair L2 graders should use fluency/grammar/**content**, not L1/age; BERT vs Whisper graders encode demographics differently from score **influence**. Audit method, not a product spec. **S10** primary.

- **F5. Employment-testing rules: job-related constructs; voice/accent only if validated.** Tippins for SIOP at EEOC (2023-01-31): AI assessments must be (1) job-related, (2) fair/unbiased, (3) reliable, (4) predictive of job outcomes, (5) documented. “Equal access to constructs”: a video interview scoring **content, facial features, and voice** must not block a person from showing job-relevant skill **unless** face/voice are shown job-related. “Equal outcomes” is **not** the professional definition of fairness; do **not** adjust scores by group membership. **S11** primary. UGESP (29 CFR 1607, still live): applies to procedures used as a **basis for employment decisions** (hire, promote, refer, license). Validity required when there is adverse impact; national origin is in scope. Interview **prep** is not a selection procedure — but if recruiters treat CodeEcho Delivery as a hiring signal, UGESP logic applies to **them**. **S12** primary. EEOC 2023 “Select Issues” AI/adverse-impact explainer was **removed from eeoc.gov in Jan 2025** (law-firm reports). Statute/UGESP unchanged. **S13** secondary.

- **F6. Free product mitigations (derived from F1–F5, not a vendor playbook).** (a) Two scores, two labels: Content = answer quality; Delivery = optional **pace dashboard** (WPM, mid-clause pauses, fillers) with “not an accent score.” (b) No composite that lets a low WPM drag a strong STAR answer. (c) No native-speaker WPM target as pass/fail; show a wide band or percentile **without** red/green shame. (d) If you keep pauses, weight **mid-clause** (F2), ignore short boundary pauses. (e) Disclose ASR uncertainty; offer **free transcript edit** before re-score (cuts F3 cascade). (f) Do **not** ship SpeechRater-style `amscore` vs native acoustic model — that *is* accent proximity. (g) Recruiter view: Content first; Delivery collapsed or omitted unless they opt in. (h) Copy: “Slower or accented English can still be a strong interview. We do not score accent.”

## Conflicts and uncertainty

- **Pause threshold conflict:** De Jong & Bosker (2013) 250–300 ms; Gao (2025) 200 ms (monologue) / 350 ms (dialogue perceived fluency); Shea & Leonard (2019, cited in Gao) 1000 ms for L2 Spanish. Do not claim one universal ms cutoff. **S3**.
- **Kwako vs Koenecke:** Kwako says AWS L1 transcription error did **not** drive speaking-score DIF (human≈BERT). Koenecke shows large **racial** WER gaps that would corrupt **token-level** filler/WPM. Different populations (K-12 EL vs US AAVE) and outcomes (holistic score vs WER). Both can be true.
- **Whisper 2026 clinical numbers (S8)** are small-n, scripted medical read-aloud, not interviews. Use for “gap persists on Whisper,” not for a WER constant.
- **Prasad 85% (S7)** is cited literature on AAVE, not their own L2 table.
- **EEOC AI pages gone (S13):** do not cite the 2023 explainer as live policy. Cite UGESP + Tippins + Title VII national-origin.
- **CodeEcho is prep, not a test.** UGESP/SIOP bind employers who **use** scores to hire, not a practice app — still the right disclosure posture.
- **Filled-pause / “um” as skill:** SpeechRater treats fillers as Delivery features; SLA also treats filled pauses as planning. No fetched paper says “count ums, ignore L2.” Do not moralize fillers.
- **Out of scope parked:** full i18n; scoring in languages other than English.

## Quotes

- S1: "a strong foreign accent does not necessarily reduce the comprehensibility or intelligibility"
- S2: "intelligible, easily understood speech even with a strong foreign accent"
- S2: "the attainment of intelligibility"
- S3: "optimal silent pause threshold for predicting L2 proficiency and perceived fluency was 200ms"
- S4: "L2 speakers pause more often within utterances than L1 speakers"
- S5: "WER… for spontaneous nonnative speech may bottom out at approximately 10%–20%"
- S6: "average word error rate (WER) of 0.35 for black speakers compared with 0.19"
- S6: "employers to automatically evaluate candidate interviews"
- S9: "BERT may exacerbate this bias; however, in practical terms… very small"
- S11: "unless facial features and voice characteristics can be demonstrated to be job-related"
- S12: "used as a basis for any employment decision"

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-1770.1995.tb00963.x | Foreign Accent… — Munro & Derwing | 1995-03 | primary | Wiley abstract+methods; full PDF paywalled |
| S2 | https://www.isca-archive.org/isaph_2016/munro16_isaph.pdf | Pronunciation learning… — Munro | 2016-03 | primary | ISAPh; accent≠intelligibility; nativeness |
| S3 | https://doi.org/10.1177/02655322251315792 | Optimal silent pause thresholds — Gao et al. | 2025-02-16 | primary | *Language Testing* 42(3); 200/350 ms |
| S4 | https://www.isca-archive.org/isaph_2022/kallio22_isaph.pdf | Pause location L2 Finnish — Kallio et al. | 2022 | primary | Mid-phrase pauses; L2 vs L1 location |
| S5 | https://files.eric.ed.gov/fulltext/EJ1202795.pdf | SpeechRater v5.0 — Chen et al. (ETS) | 2018 | primary | Delivery vs content; WER floor; fairness=group parity |
| S6 | https://www.pnas.org/doi/10.1073/pnas.1915768117 | Racial disparities in ASR — Koenecke et al. | 2020 | primary | WER 0.35 vs 0.19; acoustic; interview-eval warning |
| S7 | https://arxiv.org/abs/2205.08014 | Accented Speech Recognition — Prasad et al. | 2022-05 | primary | L2 GMU 8.2→4.0 WER; 85% is cited prior |
| S8 | https://www.nature.com/articles/s41746-026-02490-z | Accent errors + LLM remedy — npj Digit Med | 2026 | primary | Whisper β=11 pp; small-n clinical |
| S9 | https://aclanthology.org/2023.bea-1.54/ | BERT L1 DIF — Kwako et al. | 2023-07 | primary | PDF body; Δz=.025; text-only ≠ de-bias |
| S10 | https://arxiv.org/abs/2608.06300 | CAV bias in L2 graders — Wei et al. | 2026-08 | primary | Encode ≠ influence; BERT vs Whisper |
| S11 | https://www.eeoc.gov/meetings/meeting-january-31-2023-navigating-employment-discrimination-ai-and-automated-systems-new/tippins%2C%20ph.d. | Tippins / SIOP testimony — EEOC | 2023-01-31 | primary | 5 AI rules; voice job-relatedness |
| S12 | https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1607 | UGESP 29 CFR 1607 | 1978 / eCFR 2026-08-27 | primary | Employment decisions only |
| S13 | https://www.klgates.com/thought-leadership/The-Changing-Landscape-of-AI-Federal-Guidance-for-Employers-Reverses-Course-with-New-Administration-1-31-2025 | EEOC AI pages removed — K&L Gates | 2025-01-31 | secondary | Explainer gone; law not |

## Needs-browser

- https://www.siop.org/Portals/84/SIOP-AI%20Guidelines-Final-010323.pdf — fetch.py HTTP 403. Substance quoted in **S11**; PDF unread.
- https://www.isca-archive.org/isaph_2016/munro16_isaph.pdf — fetch.py exit 3 (PDF). Body used from search-saved extract (**S2**).
- Munro & Derwing 1995 full PDF — Wiley paywall (exit 2/thin HTML). Cited from abstract + Munro 2016 restatement.
- EEOC “Select Issues: Assessing Adverse Impact in Software…” — removed Jan 2025; Wayback not fetched.

## Searched

- L2 fluency automated scoring bias
- accented speech ASR error rates
- EEOC AI hiring guidance
- L2 speech rate pauses fluency
- SIOP principles employment testing
- Koenecke racial disparities ASR
- SpeechRater fairness L1 bias
- Munro Derwing intelligibility accent
