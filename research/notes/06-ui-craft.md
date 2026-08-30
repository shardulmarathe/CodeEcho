# Note — UI / visual craft / motion (recruiter 15–60s)

**Worker:** 06 · **Budget used:** 20/12 (cap 20) · **Date:** 2026-08-30 · **Scope:** Evidence-backed UI, type/composition, and motion that make a free-tier interview-prep web product look credible in the first 15–60s. Sketch/Rough.js; no design-system budget. Recruiter/portfolio audience.

**Recommendation (evidence-weighted):** Keep the sketch system. Do not restyle toward generic SaaS. Spend free craft on four checkable things: (1) above-fold plain-language “what this is” in ~10s; (2) immediate voice-state feedback (<100ms cause–effect, <400ms any wait); (3) a tiny purpose-bound motion scale with `prefers-reduced-motion` on CSS *and* JS/Rough redraws; (4) one consistent Rough.js roughness/hachure language so the UI reads finished, not template. Skip scroll-triggered fade-up theater and extra chrome (Nielsen #8 + Harley frequency).

## Findings

- **F1. First ~10s is a recruiter *match* screen, not a craft review.** Named ex-recruiter / now senior PD Emily Backes (2026-07-17): homepage must state role/level in plain language above the fold; dead links and unclear titles are red flags. She spent “ten seconds on the homepage,” then 2–3 min per case study *if earned*. She flags this as *her* pattern from hundreds of screens, “not a universal law.” For CodeEcho-as-portfolio, the product *is* the case study: say what it does (voice interview prep) in one line before any sketch flourish. **S4** primary (practitioner memoir) [opinion].

- **F2. Later readers *do* punish unfinished visuals and sameness.** Same source, three post-recruiter checks: (a) “technical designer” tests the site as a shipped product — 375px hold, real spacing scale, compressed hero; unfinished craft can stall a strong story; (b) senior designer cares about problem→decision→outcome more than polish; (c) saturated reader screens **sameness** (“fortieth portfolio” / stock structure), not skill. Neither type “forgives sameness.” Distinctive Rough.js is on-strategy; another Inter/card/gradient landing is the failure mode she names as POV-less competence. **S4** [opinion].

- **F3. Aesthetic-usability: orderly visuals raise perceived usability — with a hard cap.** Law of UX (Yablonski): users perceive aesthetically pleasing design as more usable; Hitachi 1995 (Kurosu & Kashimura) 26 ATM UIs, 252 participants — stronger correlation of beauty↔*perceived* ease than beauty↔*actual* ease. NN/G Moran (2024-02-03): attractive UI makes people “more tolerant of minor” issues, appear “orderly, well-designed, and professional”; users more likely to try the site. **Limit:** not large problems; Arcadis photos delighted once then annoyed when density blocked tasks; effect strongest when aesthetics *support* function. Recruiter implication: finished sketch = halo; broken status / mystery IA will not be forgiven. **S2** primary, **S3** primary.

- **F4. Nielsen heuristics that map to a 15–60s product glance (unchanged since 1994; page reviewed 2024-01-30).** #1 Visibility of system status: keep users informed “through appropriate feedback within a reasonable amount of time”; “ideally, immediately”; “Predictable interactions create trust.” #8 Aesthetic and minimalist: every extra unit “competes” and “diminishes” visibility of what matters — *not* a mandate for flat/generic. #4 Consistency / Jakob’s Law: people spend most time on other products; inventiveness in chrome, convention in play/stop/mic/score. #2 Real-world language (interview terms, not internal jargon). Voice-app checkable: recording / listening / scoring states must be visually obvious on first glance. **S1** primary.

- **F5. Motion signals craft when it has a named goal; noise when it is trend/whimsy/on-repeat.** NN/G Harley (2014-09-21): before adding motion, define attention location, **goal** (attract vs continuity vs relationship), **frequency** per session, **mechanics** (user-caused vs load/scroll). Peripheral motion forces a stimulus-driven attention shift; slide/self-propelled motion grabs faster than a slow fade-in-place. For non-urgent UI, “No animation at all would be the least distracting.” Cause–effect must start within **0.1 seconds** of the action (direct manipulation). Testers: “nice the first time, but now it’s getting annoying.” Unskippable menu/page zooms are “roadblocks.” Checkable: animate only user-triggered state (mic on, score reveal, error); no per-section scroll fade-up; never block a control behind a loop. **S8** primary [stale] date but mechanisms still cited as standard.

- **F6. Timing grammar that is free to copy (no Material web page readable this run).** Law of UX Doherty: interact at **<400ms** so neither side waits; give feedback in 400ms; use animation/progress to occupy waits; progress bars help “regardless of their accuracy”; a *purposeful* delay can raise perceived value/trust. Pair with Harley’s 100ms causality. Implementable token set without a DS budget: ~100ms user-caused micro; ≤400ms status/processing chrome; no decorative loops. Material M3 easing/duration page was JS-walled (exit 2) — parked. **S7** primary.

- **F7. Reduced motion is craft, not only a11y (light touch; worker 08 owns depth).** MDN (modified 2026-06-10): `prefers-reduced-motion` widely available since Jan 2020; `reduce` = minimize non-essential motion; **scaling or panning large objects** are vestibular triggers; example swaps `pulse` scale for **`dissolve` opacity**. web.dev Steiner (updated 2019-03-11): parallax / zoom / autoplay can be “medical necessity” to cut; put decorative motion behind `(prefers-reduced-motion: no-preference)`; JS Web Animations need `matchMedia` + `change` (CSS will not stop them). W3C WCAG C39 / SC 2.3.3 pages returned HTTP 403 — not used as evidence. Checkable: one CSS query *and* Rough.js/canvas/WAAPI guards; replace scale/slide with opacity/color. **S5** primary, **S6** primary (Google).

- **F8. Sketch stack is a free anti-generic texture if used as a *system*.** Rough.js (Preet Shihn, MIT): <9kB gzipped; Canvas+SVG; `roughness`, `bowing`, `strokeWidth`; fills `hachure` (default), `zigzag`, `cross-hatch`, `dots`, etc. Named adopters on the homepage include Excalidraw. This is implementable differentiation vs rounded-card SaaS *without* a design-system hire — *if* roughness/stroke are tokenized (one bowing, one hatch angle) so it reads intentional, not random doodle. Mapping sketch = “notebook/whiteboard interview” is [opinion] (Nielsen #2 applied). **S9** primary (library docs).

- **F9. What I could *not* establish from first-party sources.** No fetched recruiter study quantifies “15–60 seconds of *visual* notice” (type, composition, motion). Unread SEO/product blogs claim 6s or 8–15s scans — not cited. Unread “AI slop encyclopedia” vendors list Inter / purple-blue gradients / `rounded-2xl` / fade-up-on-scroll; those pages were not read, so slop *catalogs* are [unconfirmed]. Anti-slop recommendation rests on **S4 sameness** + **S1 #8** + keep **S9**, not on those blogs.

- **F10. Checkable free advances for CodeEcho (derived, not a source).** (a) Hero H1 = product job in recruiter English. (b) Voice status as the #1 heuristic demo (mic level / listening / scoring) with <100ms reaction. (c) CSS variables `--motion-micro: 100ms; --motion-status: 300ms;` used only where F5’s goal is answerable. (d) `@media (prefers-reduced-motion: reduce)` kills transitions *and* JS/Rough loops. (e) One roughness + one hachure angle site-wide; no third fill style on marketing chrome. (f) Zero scroll-triggered entrance animations on the landing body.

## Conflicts and uncertainty

- **Recruiter 10s vs aesthetic-usability.** S4: first 10s is req-match, “isn’t judging your Figma craft.” S3: visuals make the site look professional and raise trial. Not a numeric conflict: content-first scan *and* finished/orderly surface. Do not claim recruiters grade type/motion in 15–60s — **not evidenced**. Claim: unclear job + unfinished/generic site fail different readers (S4); pretty-but-unusable fails after (S3 Arcadis).
- **15–60s window** is the brief’s frame, not a measured recruiter SLA in any fetched primary. S4’s number is **10 seconds** homepage.
- **Harley 2014 (S8)** vs modern motion fashion: frequency/periphery/0.1s are the durable bits; “HTML5/CSS3 are new” framing is [stale].
- **Doherty purposeful delay (S7)** vs Harley “don’t waste time” (S8): delay only for *value signaling* (e.g. scoring), never for nav/menu. Record as tension, not a blend.
- **WCAG normative SC text unread** (W3C 403). Motion a11y claims here are MDN/web.dev only. Worker 08 owns depth.
- **Material duration tokens unread** (m3.material.io exit 2). Do not ship “50/150/500ms Material” as cited.
- **AI-slop pattern lists unread.** Treat purple-gradient/Inter-default as community [opinion] until a named/org page is read.
- **S4 is one designer’s hiring loops**, not industry measurement. [unconfirmed] as population claim.
- **Portfolio vs product demo:** S4 is personal portfolios. Transfer to trycodeecho.vercel.app is analogical: the live app is the artifact.

## Quotes

- S1: "Predictable interactions create trust in the product as well as the brand."
- S1: "Every extra unit of information in an interface competes with the relevant units"
- S2: "Users often perceive aesthetically pleasing design as design that’s more usable."
- S3: "making your site appear orderly, well-designed, and professional"
- S3: "A pretty design can make users forgiving of minor usability problems, but not of large ones."
- S4: "The first ten seconds are a recruiter screen, not a design review"
- S4: "The fastest way to lose me isn’t a bad case study. It’s a homepage that makes me guess"
- S4: "Sameness is what this reader is actually screening against, not skill."
- S5: "scaling or panning large objects can be vestibular motion triggers"
- S6: "reducing animations is a medical necessity"
- S7: "Provide system feedback within 400 ms in order to keep users’ attention"
- S8: "this [animation] was nice the first time, but now it’s getting annoying."
- S8: "the effect must begin within 0.1 seconds of the initial user action"
- S9: "draw in a sketchy, hand-drawn-like, style"

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/ten-usability-heuristics/ | 10 Usability Heuristics — Nielsen | 1994-04-24 / reviewed 2024-01-30 | primary | NN/G; #1 #2 #4 #8 used |
| S2 | https://lawsofux.com/aesthetic-usability-effect/ | Aesthetic-Usability Effect — Laws of UX | unknown | primary | Hitachi 1995 summary (Yablonski) |
| S3 | https://www.nngroup.com/articles/aesthetic-usability-effect/ | The Aesthetic-Usability Effect — Moran | 2024-02-03 | primary | Limits + “professional” wording |
| S4 | https://emilybackes.design/post/what-i-actually-look-at-in-a-portfolio-review | What Recruiters Actually Look At… | 2026-07-17 | primary | Named recruiter→PD; [opinion] |
| S5 | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion | prefers-reduced-motion — MDN | 2026-06-10 | primary | Scale vs dissolve; Baseline 2020 |
| S6 | https://web.dev/articles/prefers-reduced-motion | prefers-reduced-motion — Steiner / web.dev | 2019-03-11 | primary | Google; JS matchMedia; no-preference |
| S7 | https://lawsofux.com/doherty-threshold/ | Doherty Threshold — Laws of UX | unknown | primary | <400ms; progress; purposeful delay |
| S8 | https://www.nngroup.com/articles/animation-usability/ | Animation for Attention and Comprehension | 2014-09-21 | primary | Harley; 0.1s; frequency; [stale] |
| S9 | https://roughjs.com/ | Rough.js | unknown | primary | API + fill styles; Excalidraw listed |

## Needs-browser

- https://m3.material.io/styles/motion/easing-and-duration/applying-easing-and-duration — fetch.py exit 2 (thin/JS). Wanted official duration/easing tokens.
- https://www.w3.org/WAI/WCAG21/Techniques/css/C39 — HTTP 403 (exit 4). Same for WCAG22 Understanding + TR fragment. Lead: MDN/web.dev already cover the implementable query.

## Searched

- Law of UX animation
- Nielsen usability heuristics
- WCAG prefers-reduced-motion
- portfolio recruiter first impression
- aesthetic usability effect
- Material Design motion duration
- AI slop website design
