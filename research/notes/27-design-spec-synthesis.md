# Note 27 — Design spec synthesis (homepage + scorecard + recorder)

**Date:** 2026-08-30 · **Worker:** research-worker · **Scope:** implementable UI checklist from public UX sources (not Figma)

**Internal themes (not evidence):** cat 12 labeled sample + one CTA; cat 15 priming/state machine; cat 16 rubric expand + sources; Rough.js kept; ESL on Delivery.

## Findings

Numbered checklist for implementers. Each item is an external pattern; CodeEcho mapping is in parentheses.

### A. Homepage hero — one job, one CTA, sample without mic

1. **Elevator-pitch above the fold.** Communicate who you are and what users can do in one glance; treat first viewport as a gatekeeper. Users scroll only if above-fold content earns it. ([S1] 2024-03-15, primary)
2. **One-sentence tagline, not a welcome.** Start with a tagline that summarizes what the site does; cheerful “Welcome” wastes hero space. Prefer scannable, no jargon. ([S1], [S2] 2002-05-11, primary)
3. **Show a real content sample, not a category teaser.** Homepages should “reveal content through examples”: specific samples beat “Product Spotlight”-style abstractions and help users form a mental model. ([S1] §3.2, [S2] #6, primary) *(CodeEcho: labeled fixture scorecard in first viewport.)*
4. **Label the sample as a sample.** Featured content that is not representative warps the mental model of what the site offers. ([S1] §3.2, primary) *(CodeEcho: persistent “Sample / Worked example” chrome; never second-person “your score” on fixtures — that last clause is cat-12 policy, not [S1].)*
5. **One primary job; at most 1–4 starting tasks.** Emphasize a small set of high-priority tasks and keep the area around them clear. ([S2] #4, [S4] 2001-10-31, primary)
6. **Primary CTA has information scent.** Labels must say what happens on click. Generic “Click Here,” “Explore,” “Learn More” fail scent and are hard to tell apart when scanning. ([S1] §4.1, primary) *(CodeEcho: “View a sample scorecard” not “Get started” / “Allow microphone.”)*
7. **Hero image must inform, not decorate.** Users skip purely decorative graphics; stock art can mis-signal the offering. ([S1] §2.4, [S2] #10, primary) *(CodeEcho: the sample scorecard is the hero visual; Rough.js chrome is craft, not stock.)*
8. **Homepage visually distinct from interior pages.** Signpost home vs scorecard/recorder so return-from-deep-link users know they are at the start. Logo top-left as implicit Home; optional explicit Home. ([S1] §1.1–1.3, primary)
9. **No-mic path is the homepage job.** Do not open the first impression with a permission dialog. `getUserMedia` always requires a permission prompt and may never resolve if the user ignores it. ([S5] 2025-11-30, primary)

### B. Scorecard transparency — how graded / why / sources

10. **Keep the score on the primary surface.** Progressive disclosure: whatever is on the initial display is signaled as important. Hide only advanced or rarely needed material. ([S3] 2006-12-03, primary)
11. **Do not bury “how graded” if most users need it.** GOV.UK Details: use expanders to aid scan when *some* users need the extra text; **do not** hide information the majority need. ([S6], primary)
12. **One extra block → Details; many dimensions → Accordion.** Details is for a single extra section and is visually quieter than accordion/tabs. Use accordion/tabs when several peer sections must be independently opened. ([S6], primary) *(CodeEcho: overall “How this was graded” = one Details; per-dimension anchors = accordion or one Details each.)*
13. **Disclosure label has scent.** NN/g: label the control so users know what they will get. GOV.UK: short, descriptive summary text (not “More”). ([S3], [S6], primary)
14. **Expect some users to skip expanders.** GOV.UK research: some users avoid Details because they think the link leaves the page; some voice-assist tools need the control treated as a button. ([S6], primary) *(CodeEcho: put score + one-line rationale in the open chrome; rubric definitions and citation list can sit behind Details.)*
15. **Cap disclosure depth at two levels.** Designs past two levels typically lose users. ([S3], primary) *(CodeEcho: score visible → tap dimension → anchors/quotes/sources. No third nested drawer.)*
16. **Sources are secondary, not invented chrome.** Progressive disclosure says keep confusing or unused features off the first surface. ([S3], primary) *(If retrieval is empty: omit a Sources row rather than empty chips — aligns with “initial display can’t contain confusing features”; do not treat this as a citation-API finding.)*
17. **W3C APG Disclosure pattern not independently confirmed this run** (HTTP 403). Prefer native `<details>`/`<summary>` per GOV.UK HTML until APG is read. ([S6]; [S12] failed)

### C. Voice recorder — permission → priming → recording → review

18. **State machine (spec).** Browser `MediaRecorder` exposes recording control (`start`/`stop`/`pause`/`resume`) and status properties; review/playback is *app* state after assembling Blobs (individual chunks are not necessarily playable). ([S7] 2025-08-11, primary)  
    **Required app states:** `idle` → `priming` → `awaiting_permission` → `recording` | `denied` | `unavailable` → `review` → `retry` | `discard`. Do not collapse priming into `getUserMedia`.
19. **Intention tap before any prompt.** Apple audio-session guidance (recording apps): wait for the user to press Record before activating the session; ask permission explicitly rather than relying on the OS to surprise-prompt. ([S8] archive, primary, [stale] undated library doc)
20. **Priming copy on the tap target.** MDN: permission is always required the first time; the permission promise **may neither resolve nor reject** if the user ignores the prompt. ([S5], primary) *(CodeEcho: priming screen: why mic, what is stored, Cancel that aborts a hung prompt UI; then call `getUserMedia({ audio: true })`.)*
21. **Branch on Permissions API when available.** `granted` / `prompt` / `denied` — change the UI before calling `getUserMedia`. `denied` means you will not get access from JS. ([S9] last-updated 2016-08-23, secondary, [stale])
22. **Map DOMExceptions to copy, not retries.** `NotAllowedError` = insecure context, session deny, or permanent block; `NotFoundError` = no matching device; `NotReadableError` = hardware/OS failure after grant; `OverconstrainedError` can fire *before* permission (fingerprinting note). ([S5], primary) *(Denied: site-settings recovery only — no re-prompt.)*
23. **HTTPS / secure context or no recorder.** In insecure contexts `navigator.mediaDevices` is `undefined` (`TypeError`). ([S5], primary)
24. **Dual recording indicators.** Spec/MDN: browsers **must** show that a mic/camera is in use, and **must** show that permission exists even when not actively recording (e.g. Firefox pulsing red vs gray). ([S5], primary) iOS 14+: **orange** = mic in use; **green** = camera or camera+mic; orange becomes a **square** when Differentiate Without Color is on. ([S10] published 2026-05-27, primary) *(CodeEcho: in-app “Recording” + elapsed time; do not use color-only Rec; distinguish armed/permission-on vs capturing.)*
25. **Review = Blob → `<audio controls>` + explicit discard.** MDN recording flow: `dataavailable` → assemble Blob → object URL on a media element; offer Stop that calls `MediaRecorder.stop()`. ([S7], primary)
26. **Progressive enhancement: file capture.** web.dev: `<input type="file" accept="audio/*" capture>` works everywhere; desktop = file picker (`capture` ignored); iOS Safari opens Voice Memos-style recorder; Android offers an app chooser. ([S9], secondary, [stale]) *(CodeEcho: fallback when GUM denied or unsupported.)*
27. **Optional device picker is advanced.** `enumerateDevices()` can populate an audioinput `<select>`; treat as secondary disclosure, not a homepage step. ([S7], primary)

### D. Cross-cutting (all three surfaces)

28. **Keyword-first link/button names** for scan (not “CodeEcho — View sample”). ([S2] #7, primary)
29. **Keep Rough.js / visual craft off the critical path of labels.** NN/g: users dismiss over-formatted chrome as ads; meaningful graphics beat decoration. ([S2] #9–10, primary)

## Conflicts and uncertainty

- **Baymard landing/CTA:** official button-design page was JS-thin (330 chars, escalate). No Baymard premium guideline text loaded. Do not cite Baymard numbers from search snippets.
- **W3C WAI-ARIA APG Disclosure:** fetch HTTP 403. GOV.UK `<details>` is the loaded substitute; APG keyboard/ARIA specifics unverified.
- **NN/g “trust-ux” URL 404.** No separate trust/transparency article confirmed this run. Transparency items above rest on progressive disclosure + GOV.UK Details, not a dedicated “show your work” study.
- **Apple HIG “recording” page** not found as a first-party HIG URL; evidence is Support (status-bar dots) + archived Audio Session guide. Material recording indicators not fetched (budget).
- **Stripe / Linear marketing pattern articles** not fetched (budget; secondary anyway).
- **GOV.UK vs cat-16:** if rubric definitions are needed by *most* reviewers, Details is the wrong control — put a one-line “how graded” in open chrome.
- **web.dev [S9] is 2016** — Permissions API shape may have drifted; still the clearest first-party GUM-UX page loaded.
- Competitor live walkthroughs, ESL methods, ASVS, analytics vendors: out of scope.

## Quotes

- “Treat your homepage as an elevator pitch… Don’t make people guess” ([S1])
- “Specifics beat abstractions, and you have good stuff. Show some of your best…” ([S2])
- “the very fact that something appears on the initial display tells users that it's important” ([S3])
- “Do not use the details component to hide information that the majority of your users will need.” ([S6])
- “the user is not required to make a choice at all and may ignore the request.” ([S5])
- “Browsers are required to display an indicator that shows that a camera or microphone is in use” ([S5])
- “An orange indicator means the microphone is being used by an app” ([S10])

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/homepage-design-principles/ | Homepage Design: 5 Fundamental Principles | 2024-03-15 | primary | Wang; examples + CTA scent + fold |
| S2 | https://www.nngroup.com/articles/top-ten-guidelines-for-homepage-usability/ | Top 10 Guidelines for Homepage Usability | 2002-05-11 | primary | Nielsen; 1–4 tasks; show real content; [stale] width bits |
| S3 | https://www.nngroup.com/articles/progressive-disclosure/ | Progressive Disclosure | 2006-12-03 | primary | Nielsen; 2-level cap; information scent |
| S4 | https://www.nngroup.com/articles/113-design-guidelines-homepage-usability/ | 113 Design Guidelines for Homepage Usability | 2001-10-31 | primary | Date confirmed; body truncated this run |
| S5 | https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia | MediaDevices: getUserMedia() | 2025-11-30 | primary | Permission, errors, required UA indicators |
| S6 | https://design-system.service.gov.uk/components/details/ | Details – GOV.UK Design System | unknown | primary | When not to hide; details vs accordion |
| S7 | https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API | MediaStream Recording API | 2025-08-11 | primary | start/stop; Blob review; enumerateDevices |
| S8 | https://developer.apple.com/library/archive/documentation/Audio/Conceptual/AudioSessionProgrammingGuide/AudioGuidelinesByAppType/AudioGuidelinesByAppType.html | Audio Guidelines By App Type | unknown | primary | [stale] archive; wait for Record tap |
| S9 | https://web.dev/articles/media-recording-audio/ | Recording Audio from the User | 2016-08-23 | secondary | [stale]; file capture + Permissions query |
| S10 | https://support.apple.com/en-us/108331 | Orange and green indicators (iPhone) | 2026-05-27 | primary | Orange=mic; square if no-color |
| S11 | https://baymard.com/learn/button-design | Button Design – Baymard | unknown | — | THIN/JS; not used as evidence |
| S12 | https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ | APG Disclosure (Show/Hide) | — | — | HTTP 403 |
| S13 | https://www.nngroup.com/articles/trust-ux/ | (intended NN/g trust) | — | — | HTTP 404 |

## Needs-browser

- https://baymard.com/learn/button-design — fetch.py exit 2 (thin 330 chars)
- https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ — exit 4 (403); try headless or `w3c.github.io` mirror
- Not attempted (budget): Material recording indicators; Stripe/Linear marketing essays; WCAG 1.4.11/2.3.1 / WAI media-av; MDN “Using the MediaStream Recording API” (Web Dictaphone)

## Searched

- Baymard landing page CTA
- Nielsen first impressions homepage
- Nielsen progressive disclosure UX
- MDN getUserMedia permissions guide
- Apple HIG recording indicator
- GOV.UK details disclosure component
