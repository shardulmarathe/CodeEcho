# Note — Mobile and accessibility (voice-first demo)

**Worker:** 08 · **Date:** 2026-08-30 · **Scope:** Free high-ROI mobile + WCAG constraints for a voice-first SWE interview-prep web app recruiters open on phones (~390px). Constraints, not visual branding (worker 06).

**Recommendation (evidence-weighted):** Ship **WCAG 2.2 AA floors** plus **44×44 CSS px** on Record/Stop/Play and report actions. Never call `getUserMedia` on load; prime, then request `{audio:true}` from a tap. Recruiter report: real `<table>` in a labelled scroll region **or** honest cards; never color-only scores; reflow at **320 CSS px**.

## Findings

- **F1. Mic is HTTPS-only; insecure pages never prompt.** `getUserMedia()` is secure-context only. Insecure: `navigator.mediaDevices` is `undefined` → `TypeError`. Secure = HTTPS, `file:///`, or `localhost`. `NotAllowedError` also covers HTTP, user deny (session or global), and a missing Permissions Policy grant. **S1** primary.

- **F2. Only the top-level origin can ask unless the iframe is opted in.** Top-level document only, unless parent grants `microphone` / `camera` via Permissions Policy. Iframe: `allow="camera; microphone"`; header `Permissions-Policy: microphone=(self)`. Browsers may persist per-domain after first grant; must ask at least once. Spec/MDN: UA must show an in-use indicator while capturing, and an indicator that permission exists even when not recording. **S1** primary.

- **F3. Prompt can hang; permanent deny is not re-askable from JS.** Promise “may neither resolve nor reject” if the user ignores the dialog. Deny → `NotAllowedError`; no device → `NotFoundError`; granted-but-unusable hardware → `NotReadableError`. web.dev: once permanently denied, browsers honor it; recovering “intentionally takes effort.” Detect `denied` via Permissions API (where supported) and show settings steps (Chrome: address-bar site info → Site settings; may need reload). `Permissions.query()` rejects `TypeError` if the name is unsupported — wrap in try/catch; **do not treat query as ground truth on Safari.** Ground truth is `getUserMedia` resolve/reject. **S1, S4, S11** primary.

- **F4. Never ask on load; ask after a tap, with a pre-prompt; audio only.** web.dev (Chrome telemetry + research, updated 2024-06-17): “Never ask on page load or without user interaction.” Desktop: **77%** of permission prompts shown without user-intent signal, **12%** allowed; after interaction, allow rate **30%**. Users more likely to allow when they understand why and see benefit; they often dismiss while exploring. Pattern: in-page pre-prompt explaining voice scoring → user affirms → then `getUserMedia({audio:true})` (do not add `video`). Provide a path that works without mic (typed answer / skip) so a recruiter who opens a resume link is not forced into a prompt. Third-party scripts can fire unexpected prompts. **S4** primary [desktop telemetry, not mobile]. Chrome 98+ chip: camera/mic are treated as “essential”; gesture-triggered requests still get the bubble; no-gesture non-essential prompts quiet-collapse and can temporarily block. Notification allow **6.69%** / ignore+dismiss **~85%** is **notifications**, not mic — do not reuse that grant rate. **S5** primary [stale: 2022-02-01].

- **F5. Bind Record to a real click; WebKit treats display-capture as gesture-only.** WebKit `MediaDevices.cpp`: `getDisplayMedia` without user-gesture privilege rejects `InvalidStateError`. `getUserMedia` is not rejected that way in the same file, but WebKit tracks `isUserGesturePriviledged` and can withhold based on prior denials / visibility (`getUserMediaRequiresFocus`). Changeset 274206: after deny, a later **user-gesture** grant can clear the denied request so later no-gesture calls can succeed. Practical rule: Record/Stop on a `<button>` click, never `useEffect`/page-load. **S10** primary.

- **F6. Touch: WCAG AA 24×24; important controls 44×44; Android HIG 48dp.** SC 2.5.8 AA (new): pointer targets ≥ **24×24 CSS px**, or 24px-diameter spacing exception (W3C: 20×20 + 4px gap passes; 20×20 + 0 gap fails). SC 2.5.5 AAA: **44×44 CSS px**. Understanding 2.5.8: tiny isolated targets can still pass; best practice is meet the size; important controls → 2.5.5. Size is CSS px and **does not** get easier if the user zooms. Apple tips + HIG Buttons: hit target **at least 44×44 points**. Android Accessibility Help: **48×48 dp** (~9 mm; recommended 7–10 mm), **≥8 dp** gap; visual icon may be 24×24 with padding making the target 48. **S2, S3** primary; **S8, S9** primary (vendor HIG, not WCAG).

- **F7. Focus + contrast + names are the cheapest AA credibility wins.** 2.4.7 AA: visible focus. 2.4.11 AA (new): focused control “not entirely hidden due to author-created content” (sticky chrome, cookie banner, FAB, survey modal). 1.4.3 AA: text **4.5:1** (large **3:1**). 1.4.11 AA: UI identity and **states** (custom focus ring) **3:1**. 1.4.1 A: color not the only cue — red/green score chips fail. 2.4.6 AA + 3.3.2 A + 4.1.2 A: icon-only Record/Stop/Play need an accessible name and a visible label/instruction. 4.1.3 AA: recording / score-ready / mic-denied as status without moving focus. 1.4.4 AA: resize text **200%** without loss — do not lock pinch-zoom (`user-scalable=no` / `maximum-scale=1`). **S2** primary.

- **F8. Motion: auto-play is Level A; `prefers-reduced-motion` is AAA + best practice.** 2.2.2 A: auto-starting move/blink/scroll **>5 s** in parallel with other content needs an on-page pause/stop/hide (or is essential). 1.4.2 A: auto audio **>3 s** needs independent pause or volume. 2.3.1 A: no flash >3×/s. 2.3.3 AAA: interaction-triggered motion can be disabled unless essential. MDN: `@media (prefers-reduced-motion: reduce)` = user asked to minimize non-essential motion (vestibular); available since Jan 2020. Honour the MQ for score pulses / page transitions; it does **not** replace 2.2.2’s on-page control. **S2, S12** primary.

- **F9. Recruiter ~390px is wider than the WCAG reflow test (320 CSS px).** 1.4.10 AA: no two-dimensional page scroll at **320 CSS px** (≡ 1280 at 400% zoom), except parts that need 2D layout. Note 2 explicitly excepts “data tables (not individual cells)”, images, video. A 390px iPhone-class open still fails 1.4.10 if the **layout** cannot reflow at 320. Apple tips (apps, not WCAG): users should see primary content “without zooming or scrolling horizontally.” **S2** primary; **S8** secondary for web [native-HIG].

- **F10. Scorecard: labelled overflow table, or honest cards — do not `display:block` a `<table>`.** 1.3.1 A: visual relationships must be programmatic (`<table>`, `<th scope>`, `<caption>`). Roselli (user-tested vs a reflow table; 2020-11-17): wrap in `<div role="region" aria-labelledby="{caption id}" tabindex="0">` + `overflow: auto`. Maps to 2.1.1 (keyboard can focus+scroll), 4.1.2 (name+role on the focusable wrapper), 1.4.10 (scroll the **region**, not the page), 2.4.7 + 1.4.11 (3:1 focus outline). CSS `display` reflow “breaks the semantics”; ARIA cannot fully replace `headers` on spanned cells; “avoid ARIA grid roles for responsive tables.” Safer free split: (a) this scroll region, or (b) a **separate** `<dl>`/card tree at the narrow breakpoint. Pair each score with text (1.4.1). **S2, S6** primary. W3C Design System cites this pattern; W3C pages 403 via fetch.py (see Needs-browser).

- **F11. Voice chrome must be real buttons.** 2.1.1 A: all function from a keyboard except path-dependent input — Record/Stop/Play and report nav are `<button>`s, not tap-only `<div>`s. 2.1.2 A: no keyboard trap in record overlays. 2.5.7 AA (new): anything that uses dragging needs a single-pointer non-drag alternative. **S2** primary.

## Conflicts and uncertainty

- **24 vs 44 vs 48.** WCAG AA floor is 24 (2.5.8). AAA / Apple hit-target is 44. Android/Material recommend 48 dp + 8 dp gap. Understanding 2.5.8 points **important** controls at 2.5.5 (44). For Record/Play, 44 CSS px is the free alignment of WCAG AAA + Apple; 48 if matching Material.
- **Apple 44 vs 28.** Search snippets of HIG Accessibility list iOS **default** 44×44 pt and **minimum** 28×28 pt. Page was JS-walled (fetch.py exit 2). Fetched Apple **tips** and HIG **Buttons** both say hit target **at least 44×44**. Treat 28 as a native-control floor, not the web demo target, until the a11y HIG page is read.
- **Safari `permissions.query({name:'microphone'})`.** MDN lists `microphone` as queryable; `query()` throws `TypeError` if unsupported. Community iOS reports of missing API / silent `change` events remain [unconfirmed]. Do not gate UX on query alone.
- **iOS inactive-capture re-prompt (~1 min vs 10 min).** Seen only on a WebKit fork commit — [unconfirmed], not cited as fact.
- **`prefers-reduced-motion` vs 2.2.2.** W3C issue threads debate whether the MQ satisfies 2.2.2. Normative 2.2.2 asks for a *mechanism*; 2.3.3 is AAA. Do not claim the MQ passes 2.2.2.
- **Telemetry scope.** S4 77/12/30 is **desktop** permission prompts, not mobile mic. S5 ~85% ignore/dismiss is **notifications**.
- **W3C fetch.py 403** on REC, Understanding, WAI tables, W3C DS tables. REC + Understanding 2.5.8 bodies used from WebSearch full-page extracts of the same URLs. Roselli (S6) is the fetched table-pattern primary.
- Worker 06 owns aesthetics; these are constraint floors.

## Quotes

- S1: "in insecure contexts, navigator.mediaDevices is undefined"
- S1: "user is not required to make a choice at all and may ignore the request"
- S4: "Never ask on page load or without user interaction"
- S4: "77% of permission prompts on desktop are shown without a signal of user intent"
- S4: "only 12% of such prompts are allowed. After a user interaction, allow rates increase to 30%."
- S2: "at least 24 by 24 CSS pixels" (SC 2.5.8)
- S2: "at least 44 by 44 CSS pixels" (SC 2.5.5)
- S2: "not entirely hidden due to author-created content" (SC 2.4.11)
- S2: "Color is not used as the only visual means of conveying information"
- S2: "data tables (not individual cells)" excepted from 1.4.10 2D-scroll ban
- S8: "at least 44 points x 44 points so they can be accurately tapped"
- S9: "at least 48x48dp, separated by 8dp of space or more"
- S6: "this one performs better for all users" (scroll region vs CSS-reflow table)
- S6: "some browsers break the semantics" (CSS display reflow)

## Sources

id | url | title | published | tier | note
---|---|---|---|---|---
S1 | https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia | MediaDevices.getUserMedia() | 2025-11-30 | primary | fetch.py 0
S2 | https://www.w3.org/TR/2023/REC-WCAG22-20231005/ | WCAG 2.2 Recommendation | 2023-10-05 | primary | fetch.py 403; WebSearch full extract
S3 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | Understanding SC 2.5.8 | unknown | primary | fetch.py 403; WebSearch full extract
S4 | https://web.dev/articles/permissions-best-practices | Web permissions best practices | 2024-06-17 | primary | Chrome telemetry + research; desktop %
S5 | https://developer.chrome.com/blog/permissions-chip | Permissions request chip | 2022-02-01 | primary | [stale]; mic=essential; notif % only
S6 | https://adrianroselli.com/2020/11/under-engineered-responsive-tables.html | Under-Engineered Responsive Tables | 2020-11-17 | primary | W3C DS cites this; user-tested
S8 | https://developer.apple.com/design/tips/ | Apple UI Design Dos and Don’ts | unknown | primary | 44×44 pt; also “no horizontal scroll”
S9 | https://support.google.com/accessibility/android/answer/7101858?hl=en | Touch target size — Android Accessibility | unknown | primary | 48×48 dp, 8 dp gap, ~9 mm
S10 | https://github.com/WebKit/WebKit/blob/main/Source/WebCore/Modules/mediastream/MediaDevices.cpp | WebKit MediaDevices.cpp | unknown | primary | getDisplayMedia gesture; focus/visibility
S11 | https://developer.mozilla.org/en-US/docs/Web/API/Permissions/query | Permissions.query() | 2025-08-20 | primary | TypeError if name unsupported
S12 | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | prefers-reduced-motion | 2026-06-10 | primary | MQ; vestibular warning

## Needs-browser

- https://m3.material.io/foundations/designing/structure — fetch.py exit 2 (JS). Search extract: 48×48 dp; “iOS recommends 44×44dp”; 8 dp spacing. Confirm with headed/headless if citing M3 not Android Help.
- https://developer.apple.com/design/human-interface-guidelines/accessibility — fetch.py exit 2. Needed to confirm 44 default vs 28 minimum table.
- W3C 403s (fetch.py 4): TR/WCAG22, Understanding 2.5.8, Understanding reflow, https://www.w3.org/WAI/tutorials/tables/, https://design-system.w3.org/styles/tables.html. REC + 2.5.8 already extracted via WebSearch.

## Searched

- WCAG 2.2 touch target focus
- getUserMedia mobile microphone permission
- web.dev getUserMedia secure context
- Safari iOS microphone permission web
- WCAG 2.2 contrast labels reduced motion
- web.dev user media permissions prompt
- responsive table cards small screens WCAG
- WebKit getUserMedia iOS user gesture
- WAI tutorials tables responsive
- Material Design 48dp touch target
- Apple HIG minimum hit target 44
- Chrome permissions UX best practices
