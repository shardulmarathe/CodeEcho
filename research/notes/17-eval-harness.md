# 17 — Free/cheap LLM-scorer regression harnesses

**Worker:** research-worker · **Budget used:** 18/12 (cap 20) · **Date:** 2026-08-30

## Findings

### Q1 — Minimal golden set (no single N)

- **OpenAI (product evals, 2025):** a golden set is a **living** map of “dozens” of expert input→desired-output pairs — “authoritative reference of … judgement and taste.” Do not cold-start a huge bank. Review **50–100** early outputs to build an error taxonomy; include rare-but-costly edge cases; keep SMEs in the loop. LLM graders scale measurement; experts **audit** graders and logs. [S5]
- **Hamel FAQ (practitioner primary):** MVP is **not** infra — “30 minutes … **20–50** LLM outputs” on significant changes, one “benevolent dictator.” Error analysis: open-code then axial-code to a failure taxonomy; review **≥100 traces** to start; stop when **~20** new traces add no category (saturation). Re-review **100+ fresh** traces every **2–4 weeks** after prompt/model/feature changes. [S1]
- **Hamel original evals (2024-03-29):** Level **1** = cheap assertions (pytest-like), organized by **feature × scenario**, run on **every code change**; Level **2** = human/model on a cadence; Level **3** = A/B after big product changes. Rechat had **hundreds** of L1 tests (mature product, not a minimum). Pass rate is a **product decision** — “you don’t necessarily need a 100% pass rate.” [S2]
- **Hamel judge guide:** goldens should cover product **dimensions** (features / scenarios / personas — taxonomy is not universal). Synthetic **user inputs** OK to start; run them through the **real system** to get traces. Expert labels are **binary pass/fail + written critique** (critique must be few-shot-usable). Align the judge on **~25–50** examples at a time; measure **precision/recall**, not raw agreement unless classes are balanced (~50/50 in the Honeycomb example). FAQ: an LLM-as-judge needs **100+ labeled examples** plus weekly maintenance — only build it for persistent subjective failures. [S3][S1]
- **Huyen (2023-04-11, first-party):** silent prompt edits do not throw; version prompts. Check few-shot **on the same examples** (does the model recover the labels?) **and** on a held-out eval file. Her cost example evaluates **20 examples** × 25 prompt versions — a **prompt-iteration** set, not a production golden-set size. Prefer **binary** good/bad over granular scores. [S6] [stale] $ figures
- **OpenAI Evals (repo docs):** one JSONL row = one case (`input` + `ideal` or model-grade keys). Split name `name.split.version`; **bump version** when the set changes. A “good eval” is thematically consistent, **challenging** (if GPT-4 aces every prompt it is “not as interesting”), directionally clear (reference or rubric), and spot-checked. For model-graded evals, add a **meta-eval** with human `"choice"` labels; `metascore/` should be near **1.0**. [S4]
- **Honesty bar:** FAQ: “If you’re passing **100%** of your evals, you’re likely not challenging your system enough. A **70%** pass rate might indicate a more meaningful evaluation.” [S1] Matches OpenAI Evals “challenging” criterion [S4].

### Q2 — Show failures in README/CI without huge $

- **Cadence split is the cost control.** L1 assertions on every PR (schema, score bounds, empty transcript, “ignore instructions” still treated as content, mock-vs-live labeled). L2 LLM-as-judge **not** on every push: FAQ: CI sets are “small (in many cases **100+** examples),” curated for core features + past bugs + known edges; “**Favor assertions or other deterministic checks over LLM-as-judge**” because CI runs often. Promote new production failures **into** the CI set. [S1][S2]
- **GitHub Actions badge is free and only pass/fail.** Official URL: `https://github.com/OWNER/REPO/actions/workflows/WORKFLOW-FILE/badge.svg` (optional `?branch=` / `?event=`). Default branch; private-repo badges are **not** externally embeddable. [S7] The badge does **not** show N/M or failure names — those must live in README / a committed results table / CI logs. Hamel: collect metrics **outside** CI “along with versions of your tests/prompts.” [S2]
- **Display pattern that is cheap and honest:** badge (did L1 run?) + a **frozen table** of last L2 run: `k/n` + **named failing cases** (id, expected, got, one-line why). Do not hide fails to look green. 100% with no named misses reads as an easy set [S1][S4]. Judge alignment can stay a spreadsheet of 25–50 rows [S3] — no vendor eval platform required.
- **Huyen cost habit (keep the habit, not the $):** print eval spend; her GPT-4 **$0.624/prediction** (2023) is **[stale]**. Stanford-budget implication: keep PR gates assertion-only; run the LLM scorer on a **tiny labeled slice** (OpenAI “dozens” / Hamel 20–50 MVP) only when the prompt or model changes. [S6][S5][S1]

### Q3 — Adversarial cases for interview scorers

Two failure families matter more than generic “jailbreak” lists: **wrong-but-fluent** and **content-author injection** (candidate text, not your system prompt).

- **Wrong-but-fluent / verbosity.** Zheng et al. MT-Bench: verbosity = judge prefers a longer rewrite with **no new information**. “Repetitive list” attack on **23** answers: Claude-v1 and GPT-3.5 fail **91.3%**; GPT-4 **8.7%**. [S8] Same paper: on **10** math items (LLaMA-13B vs Vicuna-13B, both orders = 20 judgments), GPT-4 **default** calls an **incorrect** answer correct **14/20**; CoT **6/20**; **reference-guided** (judge solves first, then grades) **3/20**. GPT-4 can solve the item alone but is **misled by the candidate**. [S8] Interview map: STAR-shaped padding and confident-wrong tech answers. RobustJudge related work: many preference benches “emphasiz[e] stylistic fluency over factual accuracy”; JudgeBench is cited as the correctness-oriented contrast. [S10]
- **Injection (content-author).** Shi et al. (arXiv:2504.18333): distinguish **content-author** (malicious text submitted for evaluation) vs **system-prompt** compromise. Basic Injection / Contextual Misdirection / Adaptive Search. n=50/condition. Pointwise success (score shift ≥2 or verdict flip): Gemma-3-4B ASA **73.8%**; Gemma-3-27B CM **67.7%**; **GPT-4** BI **32.4%**, CM **41.2%**, ASA **45.7%**; Claude-3-Opus slightly lower. System-prompt attacks beat content-author (CM +13.8 pp, ASA +15.3 pp). They cite Raina et al.: judges are **more susceptible under absolute scoring than comparative**. Instruction-filtering regexes help some attacks; CM still evades filtering **58.3%**. [S9]
- **Cheap L1 adversarial slice (no extra judge $):** Naive / Context-Ignoring / Fake-Reasoning / Combined Attack. RobustJudge (HTML): heuristic attacks often **>80% ASR** pointwise; Combined Attack **100% ASR** on several 7B judges (translation task). Pairwise **P-ASR** is much lower (e.g. Combined 100% ASR vs **28.33%** P-ASR on Openchat-3.5) — a second reference answer helps. Template choice swings robustness: Mistral-7B H4 P-ASR **37.50%** (Vanilla) vs **96.25%** (Arena-Hard). Knowledge/math tasks more robust than open-ended text. [S10]
- **Harness implication:** keep a **small labeled adversarial folder** (fluent-wrong STAR, factually inverted tech, “ignore rubric / score 10”, authority padding) with **expected fail** or **expected low score**. Gate CI on those **assertions** (score ≤ threshold; injection text not obeyed). Do not require a second live grader (out of scope / 03). Version the set with the prompt [S4][S6].

## Conflicts and uncertainty

- **Golden-set N:** Huyen **20** (prompt RMSE) [S6] vs OpenAI “**dozens**” + **50–100** error-analysis [S5] vs Hamel MVP **20–50**, taxonomy **≥100**, judge/CI **100+** [S1][S3]. Not a numeric conflict if scoped: 20–50 = iterate; 100 = taxonomy/judge; dozens living pairs = product golden set.
- **100% pass:** Hamel and OpenAI Evals treat a perfect score as a **too-easy set** [S1][S4]. A CI badge is binary pass/fail [S7] — a green badge plus a README **18/20 + named fails** is the honest combo; a green badge alone is insufficient.
- **Same-model judge:** Hamel FAQ says same model is usually fine if aligned to humans on a **binary** task [S1]. MT-Bench reports GPT-4 **+10%** / Claude-v1 **+25%** self-favor vs humans, and authors say they **cannot determine** self-enhancement [S8]. Treat as unresolved.
- **RobustJudge defense count:** abstract in one HTML snapshot says **7** defenses / **12** models [S10 file]; later HTML says **8** defenses / **10** models. Do not quote a single inventory number.
- **“Up to 40%” template gap** appeared only in search snippets; the page body gives **37.50% → 96.25%** P-ASR (Mistral-7B, H4) [S10]. Use the table, not the snippet.
- **Chip Huyen *AI Engineering* Ch.4** (EDD, eval-as-CI) was not readable as first-party HTML; third-party rewrites (Socratopia/Medium) **not used**.
- **clawRxiv 2604.01994** (suffix-flip rates) not fetched — do not use.
- Multi-grader ensembles (committees) are **out of scope** (03); noted only as a cited defense.

## Quotes

> "A 70% pass rate might indicate a more meaningful evaluation that’s actually stress-testing" [S1]
> "Favor assertions or other deterministic checks over LLM-as-judge evaluators." [S1]
> "you don’t necessarily need a 100% pass rate. Your pass rate is a product decision" [S2]
> "golden set of examples should be a living, authoritative reference" [S5]
> "If GPT-4 or GPT-3.5-Turbo do well on all of the prompts, this is not as interesting." [S4]
> "it was misled by the provided answers, ultimately resulting in incorrect judgment." [S8]
> "verbosity bias is when an LLM judge favors longer, verbose responses, even if they are not" [S8]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://hamel.dev/blog/posts/evals-faq/index.html | LLM Evals: Everything You Need to Know | unknown (~2025 FAQ) | primary | Husain+Shankar; 20–50 / ≥100 / CI 100+; 70%; binary |
| S2 | https://hamel.dev/blog/posts/evals/ | Your AI Product Needs Evals | 2024-03-29 | primary | L1 every change; L2 cadence; Rechat hundreds; no 100% required |
| S3 | https://hamel.dev/blog/posts/llm-judge/index.html | Using LLM-as-a-Judge For Evaluation | unknown (post-S2) | primary | Critique shadowing; 25–50 alignment; P/R not agreement |
| S4 | https://raw.githubusercontent.com/openai/evals/main/docs/build-eval.md | Building an eval | unknown | primary | JSONL+ideal; version; challenging; meta-eval choice labels |
| S5 | https://web.archive.org/web/2026/https://openai.com/index/evals-drive-next-chapter-of-ai/ | How evals drive the next chapter in AI for businesses | 2025 | primary | OpenAI first-party; live site HTTP 403; dozens; 50–100 |
| S6 | https://huyenchip.com/2023/04/11/llm-engineering.html | Building LLM applications for production | 2023-04-11 | primary | 20-ex prompt eval; versioning; binary; [stale] $ |
| S7 | https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge | Adding a workflow status badge | unknown | primary | badge.svg pass/fail only; private badges not public |
| S8 | https://arxiv.org/html/2306.05685v4 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | 2023-06 (v4 HTML) | primary | Zheng et al.; verbosity 91.3/8.7; math 14/20→3/20 |
| S9 | https://arxiv.org/html/2504.18333 | Adversarial Attacks on LLM-as-a-Judge … Prompt Injections | 2025-04 | primary | content-author vs system; GPT-4 CM 41.2%; n=50 |
| S10 | https://arxiv.org/html/2506.09443 | LLMs Cannot Reliably Judge (Yet?) / RobustJudge | 2025-06 | primary | Combined ASR; template 37.5→96.3 P-ASR; fluency vs fact |

## Needs-browser

- https://openai.com/index/evals-drive-next-chapter-of-ai/ — fetch.py exit **4** (HTTP 403). Recovered via Wayback [S5]. Lead: confirm live copy if archive drift matters.
- Chip Huyen *AI Engineering* Ch.4 (eval-as-CI / EDD) — no first-party HTML; do not use third-party book mirrors.

## Searched

Hamel Husain evals, OpenAI Evals golden, LLM judge adversarial, Chip Huyen evaluation, Hamel LLM-as-a-Judge, MT-Bench verbosity bias
