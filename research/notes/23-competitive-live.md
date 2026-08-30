# 23 — Competitive live UI (browser-observable try/demo surfaces)

**Worker:** research-worker · **Budget used:** 20/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** First-party try/demo/product pages vs marketing. No ToS ingest. Login/paywall recorded as blocker, not invented UI.

## Findings

### Q1 — No-login / freemium first 1–2 screens

- **F1. No competitor showed a public scorecard or transcript without an account.** Recruiter-clickable “try/free” URLs resolve to marketing or **auth**. Observed product chrome without login: HI problem **catalog** + behavioral **session-length picker** only. [S4][S5][S6][S8][S10]

- **F2. Hello Interview “Try Design Bitly Free” is a login wall.** `/practice/overview` markets “Free to start” + Bitly CTA. `/practice/system-design` lists Bitly/Dropbox/… with Easy/Medium/Hard and “Guided Practice is only available on desktop.” Hitting `/practice/system-design/bitly` returns title **“Sign In | Hello Interview”**: “Sign in or sign up” / email or Google. **No whiteboard, rubric, report, or mic.** [S4][S5][S6]

- **F3. HI Behavioral setup chrome is public; starting is not proven.** `/practice/behavioral` (no login to view): “New Session”; modes **Micro** 1q/~5 min, **Mini** 3q/~15 min, **Full** 5–6q/~45 min; Target Company optional; Interview Level; **“Specific question Premium”**; “AI reads questions aloud.” No answer box, transcript, or scorecard in HTML. Whether “New Session” works without auth is **unconfirmed** (Bitly practice did not). [S7]

- **F4. interviewing.io AI Interviewer is login-gated.** Homepage: “Not ready to practice with a human?” / “Try our AI Interviewer” / 200+ problems “for free.” `start.interviewing.io/interview-ai` is JS-thin (exit 2). Headless: **redirect** to `start.interviewing.io/login?nextPath=%2Finterview-ai`, title “Welcome — interviewing.io”: Log In, “Not a member? Sign up.”, Continue with Google, email/password. Side quote only. **No AI session, scorecard, or mic.** [S8][S9]

- **F5. Final Round AI `/try` CTAs all go to `/sign-up`, not a session.** Visible: **FREE** badges on **General** and **Mock** only; other five formats unlabeled. Hero img alt “Interview CoPilot Interface” (screenshot, not live UI). Every primary CTA (`Try Interview CoPilot Free`, `Start Interview Prep`, `Get Started Free`) → `/sign-up`. Sign-up screen: “Create your free account”; Continue; Apple/Facebook/Google/LinkedIn/Microsoft; testimonials. **No interview type, scorecard, transcript, or mic.** [S1][S10]

- **F6. Yoodli has no public try UI in fetched HTML.** `yoodli.ai` and `app.yoodli.ai` serve the **same** enterprise roleplay marketing. CTAs “Start roleplaying” / “Get Yoodli for your team.” How-it-works: choose roleplay → start speaking → “content, delivery, and progress.” **No speaking-report sample, filler/WPM numbers, or auth URL** in extracted hrefs (buttons likely stripped / image-heavy). [S3][S11]

- **F7. Exponent public homepage is account-gated marketing.** “New: AI feedback on your interviews”; “Get started for free”; “Create your free account.” Courses / coaches / peer mocks listed. **No scorecard, voice, or session UI.** [S12]

### Q2 — AI vs human, mock vs live, cold-start

- **F8. AI vs human is labeled on marketing, not on try UI.** i.io: human mocks vs “AI Interviewer.” HI: “instant AI feedback” “tuned by FAANG interviewers”; user quotes name “LLM.” FRAI: “AI-generated questions” / CoPilot. Yoodli: all-AI roleplay. **None of the auth/first screens label a visible feedback artifact as AI- or human-authored.** [S4][S8][S1][S3]

- **F9. Mock vs live is copy, not a public toggle.** FRAI `/playground`: “AI Mock Interview is now Practice Interview inside Interview CoPilot” vs live CoPilot (homepage, note 14). Yoodli interview use-case (note 14): practice vs “Use Yoodli during your interview.” i.io: AI warmup vs booked human. **No mock/live control observed without login.** [S2][S8]

- **F10. Cold-start / wait states: none observed.** No spinner, “warming model,” or queue copy on fetched try/auth pages. HI desktop-only banner is a **device** gate, not latency. [S5][S9][S10]

### Q3 — Patterns on ≥2 products (observable)

- **P1. Free CTA → signup, not a guest session.** HI Bitly, i.io `/interview-ai`, FRAI `/try` (3/3 clicked or redirected). Exponent CTA copy matches. [S6][S9][S10][S12]

- **P2. Post-session “report/breakdown/feedback” promised; no sample scorecard in HTML.** FRAI “performance breakdown”; HI “final report with takeaways and a peer comparison”; Yoodli “View your results”; i.io “detailed, actionable feedback at the end”; Exponent “AI feedback.” Recruiter does **not** see a CodeEcho-like dual-axis card. [S1][S4][S3][S8][S12]

- **P3. Dual CTA hierarchy: free start + paid human/premium.** HI “Get Premium” + “Sign up / in”; i.io “Give it a try” + book FAANG humans; Yoodli “Start roleplaying” + “Get Yoodli for your team” / “Get a Demo”; FRAI free signup + “See pricing” on playground. [S4][S8][S3][S2]

- **P4. Mic gating not publicly observable.** FRAI “Answer out loud”; Yoodli “Start speaking”; HI “narrating your thinking.” Behavioral HI shows **TTS out** (“AI reads questions aloud”), not a mic permission gate. No browser permission UI without a session. [S2][S3][S4][S7]

- **P5. Format/problem pickers appear before scoring.** HI SD catalog + Behavioral Micro/Mini/Full; FRAI `/try` lists 7 formats (2 marked FREE). Scoring UI never appears in the public 1–2 screens. [S5][S7][S1]

## Conflicts and uncertainty

- **HI “free to start” vs Bitly login:** overview/catalog claim free Bitly; problem URL is Sign In. Unresolved whether a **new** signup can run Bitly without Premium (checkout links on overview; “Is there a free trial for Premium?” in FAQ tail unread).
- **HI Behavioral “New Session”:** lead sweep — **Start Practice** → Sign In (S14). Resolved: not guest.
- **FRAI `/try` General+Mock FREE + “no credit card”** vs homepage (note 14) “no free trial — live sessions need Pro.” Signup observed; **in-app General/Mock not observed.** Languages: `/try` “91” vs playground “143.”
- **Yoodli “Start roleplaying”:** href → `app.yoodli.ai/signup` (S13). Resolved as account gate (Chromium browser-check blocked full signup UI).
- **i.io post-login AI UI unread** (ToS/content ingest out of scope; UI also login-blocked).
- **Pramp** not fetched (budget).
- **Hero screenshots** (FRAI “Interview CoPilot Interface”; HI “System Design · Demo” video) are marketing pixels, not live product. Video not transcribed.
- Out of scope for other workers: ESL, threat model, analytics, design-spec checklist.

## Quotes

> "Guided Practice is only available on desktop." [S5]
> "Sign in or sign up" [S6]
> "Specific question Premium" [S7]
> "AI reads questions aloud" [S7]
> "Not ready to practice with a human?" [S8]
> "Create your free account" [S10]
> "Yes! You can get started for free with General and Mock interview types." [S1]
> "A final report with takeaways and a peer comparison at the end" [S4]
> "After each session, review a performance breakdown" [S1]
> "Real-time feedback on your content, delivery, and progress over time" [S3]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.finalroundai.com/try | Try Interview CoPilot Free | unknown (fetched 2026-08-30) | primary | [marketing] FREE General/Mock; CTAs → /sign-up |
| S2 | https://www.finalroundai.com/playground | Practice Interview | unknown (fetched 2026-08-30) | primary | [marketing] out-loud + debrief; no live UI |
| S3 | https://yoodli.ai/ | Yoodli homepage | unknown (fetched 2026-08-30) | primary | [marketing] enterprise roleplay; no try UI |
| S4 | https://www.hellointerview.com/practice/overview | Guided Practice overview | unknown (fetched 2026-08-30) | primary | [marketing] Bitly free CTA; peer-comparison report |
| S5 | https://www.hellointerview.com/practice/system-design | System Design Guided Practice list | unknown (fetched 2026-08-30) | primary | Public catalog + desktop gate; no session UI |
| S6 | https://www.hellointerview.com/practice/system-design/bitly | Sign In (Bitly practice) | unknown (fetched 2026-08-30) | primary | Product URL = auth wall |
| S7 | https://www.hellointerview.com/practice/behavioral | Behavioral Interview Practice | unknown (fetched 2026-08-30) | primary | Public picker; Premium on specific Q; TTS |
| S8 | https://interviewing.io/ | interviewing.io homepage | unknown (fetched 2026-08-30) | primary | [marketing] AI Interviewer vs human mocks |
| S9 | https://start.interviewing.io/login?nextPath=%2Finterview-ai | Welcome — interviewing.io | unknown (browser 2026-08-30) | primary | AI try URL redirects here |
| S10 | https://www.finalroundai.com/sign-up | FRAI Create your free account | unknown (browser 2026-08-30) | primary | First screen after /try CTA |
| S11 | https://app.yoodli.ai/ | (same as S3) | unknown (fetched 2026-08-30) | primary | App host serves marketing HTML |
| S12 | https://www.tryexponent.com/ | Exponent homepage | unknown (fetched 2026-08-30) | primary | [marketing] free account CTA; AI feedback claim |
| S13 | https://app.yoodli.ai/signup | Yoodli signup (from Start roleplaying) | 2026-08-30 | primary | Lead browser: CTA href; Chromium browser-gated |
| S14 | https://www.hellointerview.com/login?callback_url=%2Fpractice%2Fbehavioral | Sign In after Start Practice | 2026-08-30 | primary | Lead browser: Behavioral start → auth |

## Needs-browser

- ~~Yoodli “Start roleplaying”~~ — lead sweep 2026-08-30: href `https://app.yoodli.ai/signup` (S13). Headless Chromium hit browser-gate copy (“visit … on Google Chrome or Firefox”); destination URL is signup, not a guest session.
- ~~HI Behavioral “New Session”~~ — lead sweep: unlabeled start control resolves as **Start Practice** → `/login?callback_url=%2Fpractice%2Fbehavioral`, title Sign In (S14). Confirms auth wall, not guest.
- FRAI post-signup General/Mock session (requires account creation — not chased).
- HI `/practice/overview` FAQ tail unread.
- Pramp public try (unfetched).
- `start.interviewing.io/interview-ai` exit **2** — resolved via headless → login (S9).

## Searched

- Yoodli try demo interview
- Final Round AI try practice
- Hello Interview practice start free
- interviewing.io warmup try
- site:hellointerview.com Design Bitly
