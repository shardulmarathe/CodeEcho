# 14 — Competitive landscape (Yoodli, Hello Interview, Final Round AI, Google Interview Warmup)

**Worker:** research-worker · **Budget used:** 19/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** Official product/pricing/use-case pages fetched 2026-08-30. Feature/UX/price only; do not ingest HI curriculum. Vendor copy [marketing].

## Findings

### Comparison (fetched 2026-08-30)

| Product | Content / rubric | Delivery metrics | Voice | Price / free |
|---|---|---|---|---|
| **Yoodli** | Interview loop = “speaking report” (pacing, fillers). Separate Speech Coach: “content and delivery” — content **undefined**, no SWE axes. Team/Enterprise: “rubric-based scoring aligned to your **sales** methodology” [S1][S2] [marketing] | First-party blog: fillers (%), pace (WPM), eye contact, weak words [S6] | Speak/upload; follow-ups; “use during your interview… without your interviewer knowing” [S2] [marketing] | Starter: **5 lifetime** sessions (any >30s counts). Pro **$8/mo billed annually**, 10 roleplays/wk. Advanced **$20/mo billed annually**, unlimited + training-data opt-out. Team custom. Monthly $ not in HTML [S1] |
| **Hello Interview** | SWE curriculum (SD/LLD/concurrency/behavioral/coding). Practice: “rubric-based coaching”; behavioral “scored against the rubrics real interviewers use”; AI feedback on stories [S3][S7][S8] [marketing]. Do **not** ingest guides. | **None named** (no fillers/WPM/eye-contact on fetched pages) | “Narrating your thinking”; published user quote “voice option”; behavioral UI: “AI reads questions aloud” (TTS of **questions**, not candidate delivery score) [S7][S11] | Homepage: “Start free. Go deep when you're ready.” / “Learn… it's free.” Practice: “Free to start.” Premium **one-time, no auto-renew**: $47 / $79 / $279 (list $59 / $99 / $349) [S3][S8][S10] [marketing] |
| **Final Round AI** | Live CoPilot streams **private answers** (not a practice rubric). Debrief: “what worked, what to fix and how ready you sound.” Blog: “performance scores” [S4][S9] [marketing] | Blog: “speech clarity feedback” in post-interview analytics [S9] [marketing]. Homepage: 143 languages/accents | Listens live + “practice out loud.” **Stealth on by default** [S4] [marketing] | Homepage: Free $0 = Goals/materials only; “**no free trial** — live sessions need… Pro”; Pro **$25+/mo**. `/pricing` **is the homepage**. Blog (self-described “source of truth”): **no permanent free plan**; 10-min trial; $25/mo annual ($300), $60/mo quarterly ($180), $90/mo monthly [S4][S9] **conflict** |
| **Google Interview Warmup** | **Never graded** (2022 launch) [S5]. Tool **gone** from official URL | 2022: job-related terms, most-used words, talking-point time (experience/skills/goals) — patterns, not grades [S5] | Was live transcription of spoken answers [S5]. Now: page points to **Gemini Live** [S12] | Was free. `grow.google/interview-warmup` = article **11 Dec 2025**, not a tool [S12]. `interviewwarmup.withgoogle.com` = **HTTP 404** [S13] |

### Per-product

- **F1. Yoodli is delivery-first.** Official interview page names pacing + filler words as the speaking-report examples. 2023-01-16 blog adds eye contact, weak words, filler %, WPM (Musk demo: 42 fillers, 5%, 172 WPM). No fetched page lists SWE/STAR/Code-Solve-Communicate axes. “Content” appears only as Speech Coach marketing. Live-nudge-in-real-interview is first-party copy [S2][S6] [marketing].

- **F2. Yoodli free cap is lifetime, not monthly.** FAQ: Starter 5 lifetime; Pro 10/week; Advanced unlimited. Annual $8 / $20 in FAQ. Team rubric language is sales-enablement, not SWE interview [S1].

- **F3. Hello Interview is paid SWE curriculum + guided practice, not a delivery coach.** Pricing/premium: courses + Guided Practice (SD, LLD, AI Coding) + AI tutor + question library. Behavioral GP: AI feedback after answers; TTS “AI reads questions aloud.” No delivery-metric product claims. Free surface = learn + “free to start”; full GP library is Premium [S3][S7][S8][S10][S11] [marketing].

- **F4. HI price/library copy disagrees across official pages.** Promo $47/$79/$279 vs list $59/$99/$349 (pricing + premium). Practice overview + homepage show **list** $59/$99/$349 and library “**12,000+**”; pricing + premium show “**5,000+**” / Premium stats “**5.2k** Reported Interview Questions” [S3][S7][S8][S10].

- **F5. Final Round AI’s paid core is stealth live copilot, not honest practice grading.** Homepage: listen → private suggested answer; Stealth default; Free = Goals only; live = Pro $25+/mo, “no free trial.” Practice + auto debrief listed under Pro. Recruiter-hostile if used in a real loop [S4] [marketing].

- **F6. FRAI free-tier conflict (same vendor).** Homepage/FAQ: free plan exists (Goals); “no free trial” for live. Blog S9: “no permanent free plan”; 10-minute trial; $25/$60/$90. Prefer homepage for current product split; treat blog dollar schedule as [marketing] until a checkout page is read (JS). [S4][S9]

- **F7. Interview Warmup official status (2026-08-30):** Practice tool is **not** at the official URL. Grow page is “How to Prepare for an Interview,” dated **December 11, 2025**, pointing to Gemini Live + Career Dreamer. Old host **404**. 2022-06-02 launch: transcribe + ML patterns; “Your responses aren’t graded or judged.” No first-party sunset post fetched. Third-party “April 2026” retirement **unread** → [unconfirmed]. [S5][S12][S13]

- **F8. Free SWE-rubric + delivery + voice gap.** Among these four, no fetched offer is **free and complete** on all three: (a) SWE-specific content rubric, (b) delivery analytics, (c) candidate voice in. Yoodli: (b)+(c), 5-session cap, no SWE rubric. HI: (a) on paid GP / free learn, voice = narrate/TTS not delivery score. FRAI: paid stealth + qualitative debrief; free = prep only. Warmup: vacant; never did (a). Gemini Live is a general chatbot pointer, not a SWE grader [S1][S2][S4][S7][S12].

## Conflicts and uncertainty

- **FRAI free/trial:** homepage Free Goals + no live trial vs blog no free plan + 10-min trial [S4][S9].
- **FRAI Pro dollars:** homepage “$25+/mo”; blog $25/$60/$90. Checkout UI unread (Needs-browser).
- **Yoodli monthly sticker:** toggle in DOM; amounts not in fetched HTML. Reviews quoting other $ ignored (unread).
- **HI library 5k vs 12k** and promo vs list prices: both official, unresolved.
- **Warmup sunset month:** official = Dec 2025 tips page + 404 host. April 2026 blogs not fetched.
- **HI voice scoring:** TTS + user “voice option” quote ≠ delivery metrics. Behavioral page thin (1160 chars); more UI may be JS.
- **Yoodli “content”:** marketing noun only on fetched pages.
- **Do not scrape** HI/i.io into a KB (ToS). This note uses marketing/feature chrome only.

## Quotes

> "speaking report with analytics such as pacing and filler words" [S2]
> "Use Yoodli during your interview in private and get nudges" [S2]
> "The Starter plan includes 5 lifetime sessions" [S1]
> "Pro ($8/month billed annually)" [S1]
> "Your responses aren’t graded or judged" [S5]
> "There is no free trial - live sessions need an active Pro subscription." [S4]
> "Stealth Mode is on by default." [S4]
> "AI reads questions aloud" [S11]
> "There is no permanent free plan." [S9]
> "scored against the rubrics real interviewers use." [S7]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://yoodli.ai/pricing | Yoodli Pricing & Plans | unknown (fetched 2026-08-30) | primary | [marketing] FAQ $8/$20 annual; 5 lifetime |
| S2 | https://yoodli.ai/use-cases/interview-preparation | Yoodli AI Interview Coach | unknown (fetched 2026-08-30) | primary | [marketing] delivery + live nudge |
| S3 | https://www.hellointerview.com/pricing | Hello Interview Pricing | unknown (fetched 2026-08-30) | primary | [marketing] $47/$79/$279; 5,000+ |
| S4 | https://www.finalroundai.com/ | Final Round AI homepage | unknown (fetched 2026-08-30) | primary | [marketing] Free Goals; Pro $25+/mo; stealth |
| S5 | https://blog.google/company-news/outreach-and-initiatives/grow-with-google/interview-warmup/ | Helping job seekers prepare (Warmup launch) | 2022-06-02 | primary | No grades; patterns only |
| S6 | https://yoodli.ai/blog/how-to-stop-using-filler-words | How to Stop Using Filler Words | 2023-01-16 | primary | Delivery metrics; not SWE |
| S7 | https://www.hellointerview.com/practice/overview | Hello Interview Guided Practice | unknown (fetched 2026-08-30) | primary | [marketing] rubric coaching; 12,000+; list $ |
| S8 | https://www.hellointerview.com/premium | Hello Interview Premium | unknown (fetched 2026-08-30) | primary | [marketing] 5,000+ / 5.2k; $47–$279 |
| S9 | https://www.finalroundai.com/blog/final-round-ai-pricing | Final Round AI Pricing (blog) | unknown (fetched 2026-08-30) | primary | [marketing] claims “source of truth”; conflicts S4 |
| S10 | https://www.hellointerview.com/ | Hello Interview homepage | unknown (fetched 2026-08-30) | primary | [marketing] Start free; 12,000+ |
| S11 | https://www.hellointerview.com/practice/behavioral | HI Behavioral Practice | unknown (fetched 2026-08-30) | primary | [marketing] TTS; thin page |
| S12 | https://grow.google/interview-warmup | How to Prepare for an Interview | 2025-12-11 | primary | Tips + Gemini Live; not a tool |
| S13 | https://interviewwarmup.withgoogle.com | (former Warmup host) | n/a | primary | fetch.py HTTP 404 2026-08-30 |

## Needs-browser

- Yoodli `/pricing` monthly vs annual dollar amounts (JS toggle; FAQ annual only). Exit 0 but incomplete.
- FRAI live checkout / “See all plans” ( `/pricing` served homepage HTML). Needed to resolve S4 vs S9.
- HI `/practice/behavioral` may hide answer-input/voice-mic behind JS (1160 chars).

## Searched

- Yoodli interview pricing
- Hello Interview pricing
- Final Round AI pricing
- Google Interview Warmup status
- Yoodli speaking report analytics
- site:finalroundai.com pricing plans
- Hello Interview guided practice voice
