# Note 02 — Substance / depth detection (vague, empty rhetoric)

**Worker:** research-worker · **Date:** 2026-08-30 · **ROOT:** /Users/shar/Documents/GitHub/CodeEcho

## Findings

- **Recommendation (from sources below):** treat “no substance” as a **heuristic span layer** (lexicon + named-entity/number density + question-term overlap), then fold observable checks into the **existing Communication/Specificity** judge. Do **not** add a new rubric dimension and do **not** add a second LLM pass on a shared free-tier budget. Whisper word timestamps can highlight cheap-flagged spans with no new API.

- **[S1] Google Interview Warmup (official, 2022-06-02, primary):** Insights were *pattern surfaces*, not grades. Named signals: job-related terms, most-used words, talking-point coverage (experience / skills / goals) and time on each. Quote: "Your responses aren't graded or judged." Cheap analog: term lists + word-freq + coarse topic tags. No depth/substance judge.

- **[S6][S7][S8][S9] Yoodli first-party:** Delivery analytics, not answer depth. Homepage [S6][marketing] says results include "content, delivery." Blogs define countable delivery: fillers (`um`, `uh`, `like`, `ah`, `well`), filler phrases (`you know`, `I mean`, `I guess`, `you see`), "weak words" (unnamed list), pace, eye contact, talk time [S7][S8]. Goal: "<3% filler words" [S9]. Musk example: 42 fillers, 5% of speech, 172 WPM [S7]. Conciseness advice is rhetorical (cut fillers, slow down), not a content scorer [S8]. Overlaps CodeEcho Delivery; does **not** implement empty-rhetoric detection.

- **[S10] Final Round AI debrief (vendor blog, [marketing]):** Claims post-session compare to "structured model answers"; flags "missing result metric," "thin action," qualitative vs quantitative result; behavioral map to competency/LP; practice scores STAR, "specificity of the result," competency relevance. No published cue lists, thresholds, or eval. Implies a **second LLM vs gold answer** — not free-tier cheap, not a local heuristic.

- **Speechify coaching / interviewing.io content-quality metrics:** not established here (no first-party page read).

- **Concrete “no substance” signals (NLP, not interview products):**
  - **Hedges (uncertainty):** CoNLL-2010 [S3] cues: auxiliaries (`may`, `might`, `could`); speculative verbs (`suggest`, `seem`, `appear`); adj/adv (`probable`, `likely`); complex phrases (`raises the question of`). Task 1 = sentence uncertain if ≥1 cue; Task 2 = cue + syntactic scope. Domain is bio IE + Wikipedia, not interviews.
  - **Weasels / empty rhetoric (closest named construct):** [S3] Wikipedia: "impression that something important has been said" but content is "vague, misleading, evasive or ambiguous"; no source/backup. Groups: uncertainty adj/adv; generalization (`generally`, `widely`); qualifiers/superlatives (`excellent`, `best`); obviousness (`clearly`); dummy-subject passives (`It is claimed`); `there is evidence that`; numerically vague (`some`, `many`, `most`, `experts say`). Cue presence ≠ weasel (context-dependent).
  - **Vagueness vs detail (cheap numeric):** VAGO [S2] lexicon (~1,640 EN/FR terms): approximation, generality, degree, combinatorial. Sentence vagueness = vague-token / N; subjectivity = degree+combinatorial / N. Early version treated “precise” as *no* vague markers (same score for an NE-rich sentence and a slogan). Fix: **detail/vagueness** = `|P| / (|P|+|V|)` where P = spaCy named entities (people, places, times, orgs, **numbers**). Text score = mean of sentence ratios. Zero extra LLM. Interview analog: metrics/names/dates vs hedge-adj density.
  - **Not found as named product detectors:** first-person ownership, topic drift, circular restatement. Closest cheap proxies: first-person + past action verbs (rule); sentence↔question token overlap (drift); sentence↔rest-of-answer overlap (circularity). Unvalidated for interviews.
  - **Hedge ≠ empty answer:** [S3][S11] hedges mark *uncertainty*; a specific “I might have reduced p95 by 40%” is hedged and high-substance. Do not score hedges alone as no-depth.

- **Detection approaches and cost:**
  1. **Rule/lexicon (cheapest, free-tier):** CoNLL-style cue lists + VAGO-style NE/number ratio + regex for `%`, `$`, integers + Warmup-style job-term/talking-point counts. Span-level; align to Whisper timestamps. False positives on justified hedges [S3][S11]. Early hedge work used hand lists and n-grams [S3][S11].
  2. **Supervised/neural hedge taggers:** CoNLL systems; later joint word+POS models report 69.74 F1 on CoNLL-2010 Wikipedia [S11]. Needs labeled data + a model host — **new infra**, out of budget unless a tiny on-device list is enough.
  3. **Embeddings / lexical overlap:** G-Eval table [S4] SummEval **Relevance**: BERTScore Spearman ρ=0.312 vs G-Eval-4 ρ=0.547. Cheap similarity is a weak relevance proxy, not a substance detector. Usable only as a drift/restatement *hint*.
  4. **LLM judge (quality, $):** G-Eval [S4]: criteria + auto CoT steps + form-fill score. Best human corr on SummEval is GPT-4 (avg Spearman **0.514**); GPT-3.5 **0.401**. GPT-4 path used `n=20` samples to estimate score probs. CoT helps; judges biased toward LLM-written text. Task is summarization/dialogue, not interviews. Chrome [S5]: prefer **binary PASS/FAIL** (mid-scale clustering / polite inflation); one criterion per judge; rationale **before** label; few-shot; temp≈0; JSON `{rationale, label}`. Start large then shrink; mix cheap daily + strong release judges. A **second** substance pass doubles tokens vs folding span quotes into the existing Specificity prompt.
  5. **Speech analytics beyond fillers:** Yoodli pace / eye contact / weak words [S7][S9] = delivery. No first-party content-depth metric.

- **Architecture vs CodeEcho:** Delivery already covers fillers/WPM/pauses. Adding hedge% as Delivery duplicates Yoodli and misses weasels-with-metrics. A **9th dimension** would re-ask Specificity (worker 01 owns count). A **second LLM pass** matches FRAI’s model-answer compare [S10][marketing] and G-Eval cost [S4] — wrong for shared free-tier. **Heuristic layer + existing judge** matches Warmup (show patterns, don’t grade) [S1] and VAGO (local scores) [S2]; optional: pass flagged sentences into the current rubric as evidence so one call can quote empty spans.

## Conflicts and uncertainty

- [S6] homepage “content” vs [S7][S8][S9] blogs that only specify delivery counts. Treat “content coaching” as [marketing] until a metric page is read.
- FRAI “missing metric / STAR specificity” [S10] is vendor copy; no independent eval.
- VAGO “detail” is news/opinion NE density, not SWE interview depth (tradeoffs, I-owned actions). Transfer is analogical.
- Weasel/hedge cues are context-dependent [S3][S11]; lexicon FPs on careful technical hedging.
- G-Eval 0.514 is summarization, not interview substance; GPT-4 + multi-sample scoring is not free-tier.
- Chrome “research shows” mid-scale clustering [S5] is [nameless] (no paper named on the page).
- Apple model-judge docs [Needs-browser]: fetch.py exit 2.
- Warmup retirement / Speechify / interviewing.io content scores: not established (no first-party read).
- “I” ownership, topic drift, circular restatement: no public interview-product detector found.

## Quotes

- [S1] "Your responses aren't graded or judged"
- [S3] "impression that something important has been said, but what is really communicated is vague"
- [S3] hedges: "authors do not or cannot back up their opinions/statements with facts"
- [S4] G-Eval-4 SummEval avg Spearman 0.514 (table)
- [S5] "We recommend using binary labels."
- [S6] "Real-time feedback on your content, delivery, and progress over time"
- [S9] "fewer than 3% filler words is considered a normal part of communicating"
- [S10] "missing result metric, a thin action section, a result that was qualitative"

## Sources

id | url | title | published | tier | note
--- | --- | --- | --- | --- | ---
S1 | https://blog.google/company-news/outreach-and-initiatives/grow-with-google/interview-warmup/ | Helping job seekers prepare for interviews | 2022-06-02 | primary | Official Warmup: patterns, no grades
S2 | https://arxiv.org/html/2309.06132 | Measuring vagueness and subjectivity: VAGO | 2023-09 (arxiv) | primary | Lexicon + spaCy NE detail ratio
S3 | https://aclanthology.org/W10-3001.pdf | CoNLL-2010 hedge/weasel shared task | 2010-07 | primary | HTML landing was metadata; facts from paper PDF body
S4 | https://arxiv.org/html/2303.16634 | G-Eval: NLG eval with GPT-4 | 2023-05-23 (v3) | primary | CoT judge; GPT-4 vs 3.5; BERTScore weaker
S5 | https://developer.chrome.com/docs/ai/evals/judge-basic | Set up a basic judge model | unknown | primary | Binary, rationale-first, one criterion
S6 | https://www.yoodli.ai/ | Yoodli homepage | unknown | low | [marketing] “content, delivery”
S7 | https://yoodli.ai/blog/how-to-stop-using-filler-words | How to Stop Using Filler Words | 2023-01-16 | secondary | First-party filler/weak-word/pace
S8 | https://yoodli.ai/blog/say-more-with-less-how-to-speak-more-concisely | Say More with Less | 2023-05-10 | secondary | Conciseness tips, not a scorer
S9 | https://yoodli.ai/blog/yoodli-skill-reduce-um-filler-words | Yoodli Skill: Reduce um filler words | 2023-08-30 | secondary | <3% filler goal
S10 | https://www.finalroundai.com/blog/interview-copilot-debrief | Interview CoPilot Debrief | unknown | low | [marketing] model-answer + metrics
S11 | https://arxiv.org/pdf/2405.13319 | Hedge Detection in Text (Katerenchuk & Levitan) | 2024-05-22 | secondary | 69.74 F1 Wikipedia; hedges ≠ always empty

## Needs-browser

- https://developer.apple.com/documentation/evaluations/designing-effective-model-judges — fetch.py exit 2 (JS-walled). Search claimed observable score levels vs “good/very good”; unverified.

## Searched

- Yoodli interview content quality
- hedge detection NLP vagueness
- Google Interview Warmup scoring
- Yoodli hedging phrases metrics
- LLM judge specificity scoring
- site:yoodli.ai filler hedging
- Final Round AI interview scorecard
