# 12 — Homepage / no-mic demo patterns

**Date:** 2026-08-30  
**Worker:** research-worker  
**Scope:** Evidence-backed homepage IA, sample-result / no-permission demos, and ethics of labeled fixtures vs fabricated personal scores. Recruiter path. Out of scope: Rough.js (06), auth walls (10), competitive feature matrix (14).

## Findings

### F1 — First viewport must state identity + value in ~10s; ask later [S1][S2]
- Users decide stay/leave in the first ~10s; value proposition must be clear in that window or they bounce. After ~30s the leave-rate flattens. [S2] primary, 2011-09-11.
- System 1 judges aesthetics by ~50ms (Lindgaard et al., cited by NN/g) and shapes perceived relevance, usability, and credibility. [S1] primary, 2017-10-01.
- First-viewport IA implications from NN/g (not a 3-block template, but constraints): (a) **who you are / what you do** in a concise prominent statement; (b) visually prioritize the persona’s first-step workflow; (c) **one** salient CTA — competing equal-weight CTAs force System 2 and feel like strain; (d) **do not** lead with registration / permission asks — “provide value first.” [S1]
- Explicit anti-pattern: homepage that immediately demands contact info, app download, *and* browser notification permission — NN/g calls this “needy” and credibility-eroding. Maps to CodeEcho: do **not** ask for mic permission in the first viewport. [S1]
- Avoid the phrase “Get Started” — NN/g says it “prematurely stops users” and diverts them from other needed information. [S1] [unconfirmed as still current; 2017]
- Recruiter implication: first viewport should communicate “spoken interview practice → scored rationale” *and* show proof, without a permission prompt.

### F2 — First-use empty states: explain the filled state + one next action [S3]
- IBM Carbon (v10, fetched 2026-08-30; pub date unknown): empty states exist to show “what the user would see if they had data” plus a constructive next step. Anatomy: optional image, short title (prefer positive), body (why empty + benefit of acting), optional primary action, optional secondary (docs). [S3] primary (design system).
- First-use / no-data goal: user understands what will appear *and* how to add it. Keep one focus; don’t cover multiple options in one empty state. Don’t use product-specific jargon yet. [S3]
- Carbon **starter content**: pre-built sample data so users “dive in and learn… with sample data,” “tinker, examining and deleting… without serious consequences.” Optional personalization “adds to the positive experience.” If starter content can be deleted, keep a basic empty state as backup. Tidwell cited: explore, back out, try again without stress. [S3]
- Carbon **in-line docs** for a primary feature may include “an image of the space populated with data” to trigger interest. Keep to one feature. [S3]
- Carbon **onboarding tours** are optional and must sit *with* a basic empty state, not replace it. [S3]

### F3 — Homepage IA (NN/g 2024): identity → examples → action [S4][S5][S6]
- Five principles (2024-03-15): (1) easy access to homepage; (2) communicate who you are / what you do; (3) **reveal content through examples**; (4) prompt actions; (5) keep simple. [S4] primary.
- First viewport = elevator pitch. Tagline must say what the site does; generic “welcome” wastes hero space. Unique value answers “why this over others.” Speak user language, not feature jargon. Imagery must be informative, not stock decoration. [S4]
- **Examples beat abstractions**: “specific examples of your site’s content” above the fold; category labels without samples fail. Users scroll only if above-the-fold content earns it. Avoid false floors / full-bleed images with no cue of more below. [S4][S6]
- 2002 guideline still restated: “Show examples of real site content. Don’t just describe… Specifics beat abstractions.” [S6] [stale] year but congruent with 2024 P3.
- CTAs: high information scent; avoid “Click Here / Explore / Learn More / Get Started.” Generic “Get Started” attracts clicks into signup/quiz funnels, creates illusion of completeness, and users stop scanning for About info. Reciprocity: give information before asking for personal data. [S4][S5]
- Recruiter-path mapping: first viewport = problem (spoken interview answers are hard to evaluate) + **visible sample scorecard** (proof) + one specific CTA (e.g. “View a sample scorecard” / “Try a written example”) — not “Get Started” into mic permission.
- Keep homepage simple: predictable layout; minimize motion (moving elements read as ads); no autoplay video; tagline visible immediately (don’t animate it in). Popups/splash before value are “among the top most hated”; only acceptable pre-content splash is legal consent (cookies/age). Reciprocity again: offer value before requesting anything. [S4]
- Google bounce research cited by NN/g: bounce likelihood +32% when load goes 1s → 3s. [S4] [secondary citation]

### F4 — No-mic proof pattern: recorded / fixture library, not live capture [S8]
- interviewing.io `/mocks` (fetched 2026-08-30; pub unknown): a public library of mock-interview **replays**. Intro states interviews are “shared with permission from both participants, with the intent of helping others learn.” Sessions use anonymous handles (e.g. “Lexical Panda interviewed Wily Tornado”), company-role labels, problem titles. Visitor watches existing output — no mic/camera required to evaluate the product. [S8] [marketing] for “100K / 10K” counts; the **pattern** (permissioned recordings + pseudonyms) is on-page.
- Maps to CodeEcho: ship a **frozen fixture scorecard** (real grader output on a canned answer) as the first-viewport example; optional “play sample audio” that never requests `getUserMedia`. Recruiter path = watch/read, not speak.
- Carbon’s starter-content + in-line “image of the space populated with data” is the in-app twin of this homepage pattern. [S3]
- Homepage first viewport of interviewing.io itself not fully read this run — see Needs-browser.

### F5 — Ethics: labeled sample is honest; “your score” without a session is deceptive [S7][S9][S10]
- NN/g deceptive-pattern definition (2023-12-01): design that prompts an action benefiting the company by “deceiving, misdirecting, shaming, or obstructing.” Walkthrough checks include: is presented information **factually correct**? could users **easily misinterpret** choices? are they rushed or emotionally pressured? [S9] primary.
- Persuasion vs deception hinge: social proof / anchoring is OK **“assuming the content is accurate and not fabricated.”** Fabricated proof is the line. [S9]
- **Nagging** includes repeatedly triggering a permission request until the user gives up — anti-pattern for mic. [S9]
- FTC 16 CFR §255.2 (eCFR current as of 2026-08-27; source 88 FR 48102, 2023-07-26): an endorsement about a key attribute is read as **typical** of what users generally achieve; if not substantiated, disclose **generally expected** performance so the **net impression** is not misleading. “Results not typical” / “you are not likely to have similar results” was **empirically insufficient**. If people are implied to be actual consumers, they must be, or disclose they are not. [S10] primary.
- FTC Consumer Reviews & Testimonials Rule (effective 2024-10-21): fake/false testimonials that misrepresent that the speaker exists, used the product, or had the stated experience are prohibited when the business disseminates them. [S7] primary.
- Application (analogical, not a decided case): a fixture labeled **“Sample scorecard — not your session”** is starter content. A UI that says **“Your score: 87”** when the visitor has not spoken fabricates a personal result (false experience) and, if a high score is used as proof, can also imply typical outcomes without substantiation. A tiny “example” footnote does not reliably fix net impression ([S10] typicality research).
- Honesty bar for CodeEcho: persistent “Sample / Example / Worked example” chrome; no second-person (“your”) on fixture scores; one real canned run (same grader path); do not present fixture as a recruiter’s own evaluation or as typical candidate scores; ask for mic only after proof, once, with a no-mic alternative.

## Conflicts and uncertainty

- No NN/g or gov page was found that literally specifies “label sample data vs fabricate your-score.” Ethics here are assembled from Carbon starter content + NN/g deception tests + FTC typicality/fake-testimonial rules. Analogical, not a CodeEcho-specific ruling.
- FTC §255.2 governs **advertising endorsements**, not in-product fixtures. A homepage scorecard used as proof of product quality is closer to an ad claim than an empty-state seed. [speculation] on enforcement.
- Carbon allows “some personalization” of starter content; that conflicts with a hard “never say your” rule if personalization implies the fixture belongs to the visitor.
- interviewing.io homepage hero/CTA not page-read; `/mocks` is the evidence for the no-live-input pattern. Feature claims on that site are [marketing].
- Competitive interview-prep homepages (Exponent, Pramp, etc.) and speech-tool sandboxes (Whisper, Otter, Descript sample project, Mixpanel demo) were not page-read — parked.
- Empty-state blogs (Kompassify, Appcues, AuditBuffet) appeared in search; not used as evidence.

## Quotes

- “To gain several minutes of user attention, you must clearly communicate your value proposition within 10 seconds.” [S2]
- “Don’t ask for too much, too early.” / “provide value first” [S1]
- “Reveal Content Through Examples” / “specific examples of your site's content” [S4]
- “Users can tinker, examining and deleting content without serious consequences.” [S3]
- “assuming the content is accurate and not fabricated, then the design is persuasive, not deceptive.” [S9]
- “Results not typical” … “is insufficient to prevent this ad from being deceptive” [S10]
- “All interviews below are shared with permission from both participants” [S8]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/first-impressions-human-automaticity/ | First Impressions Matter (Fessenden) | 2017-10-01 | primary | 50ms aesthetics; one CTA; no early asks |
| S2 | https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages/ | How Long Do Users Stay on Web Pages? (Nielsen) | 2011-09-11 | primary | 10s value prop; Weibull dwell |
| S3 | https://v10.carbondesignsystem.com/patterns/empty-states-pattern/ | Empty states – Carbon Design System | unknown | primary | starter content; first-use anatomy |
| S4 | https://www.nngroup.com/articles/homepage-design-principles/ | Homepage Design: 5 Fundamental Principles | 2024-03-15 | primary | identity → examples → action |
| S5 | https://www.nngroup.com/articles/get-started/ | “Get Started” Stops Users | 2017-08-20 | primary | generic CTA / reciprocity |
| S6 | https://www.nngroup.com/articles/top-ten-guidelines-for-homepage-usability/ | Top 10 Guidelines for Homepage Usability | 2002-05-11 | primary | [stale] year; “show examples” |
| S7 | https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers | FTC Reviews & Testimonials Rule FAQ | 2024-11-08 | primary | fake testimonials; rule 2024-10-21 |
| S8 | https://interviewing.io/mocks | Mock Interview Replays | unknown | secondary | [marketing] counts; permissioned fixtures |
| S9 | https://www.nngroup.com/articles/deceptive-patterns/ | Deceptive Patterns in UX (Rosala) | 2023-12-01 | primary | fabrication line; nagging permissions |
| S10 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.2 | 16 CFR §255.2 Consumer endorsements | 2023-07-26 | primary | typicality; net impression |

## Needs-browser

- https://interviewing.io/ — homepage first-viewport IA (hero/CTA); fetch of `/mocks` skipped the marketing chrome. Exit: not fetched (budget).
- Speech-tool “sample project / playground without mic”: OpenAI Whisper, Otter, Descript — not page-read.
- Mixpanel / similar analytics live-demo sandboxes — not page-read.
- Atlassian / Polaris empty-state pages — not page-read (Carbon covered the design-system slot).

## Searched

- NN/g first impressions landing page
- NN/g empty state sample data
- NN/g homepage value proposition CTA
- labeled sample data demo mode UX
- FTC deceptive fake testimonials sample
- NN/g dark patterns fake personalization
- NN/g deceptive design patterns
- interviewing.io watch mock interview
- FTC endorsement typical results disclaimer
