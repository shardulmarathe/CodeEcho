# Note — Voice / recorder UX (interview practice)

**Worker:** 15 · **Date:** 2026-08-30 · **Scope:** Recorder interaction design for interview-practice web (desktop + mobile): state machine, clipping/silence/permission UI, free Web Audio level meters. Not WCAG 44px (08), not STT error enums (07), not no-mic homepage fixtures (12).

**Recommendation (evidence-weighted):** UI states = MediaRecorder `inactive`/`recording`/`paused` plus app `priming` (pre-prompt) and `review` (play + retry). Ask `{audio:true}` only after a tap; after deny show site-settings recovery, never re-prompt. Meter with AnalyserNode + rAF; clip warn on `getFloatTimeDomainData` |x|≥1. Max duration and countdown are app timers (`stop()`), not API. Silence UX is not documented in primaries — derive from a near-zero meter.

## Findings

- **F1. Browser recorder states are only `inactive` | `recording` | `paused`.** MDN `state`: `inactive` = “not occurring — it has either not been started yet, or it has been started and then stopped”; `recording` = started and UA capturing; `paused` = started then paused, not yet stopped or resumed. `pause()`/`resume()` on `inactive` throw `InvalidStateError`; calling the method that matches the current state is a no-op. No spec `review` / `countdown` — those are app states around `getUserMedia` + `start()`/`stop()`. **S1, S4** primary.

- **F2. Canonical web clip flow: Record (red) → Stop → review clip (`<audio controls>` + Delete).** Web Dictaphone (MDN): `getUserMedia({audio:true})` first; on Record `start()` and paint control red; on Stop `stop()` and clear chrome; `onstop` builds Blob from chunks, `URL.createObjectURL`, `<audio controls>`, name prompt, Delete. After stop, `state` is `inactive`. Recording also ends if the mic stream ends (user revoked / track stopped). Chunks from `dataavailable` are not individually playable until reassembled. Fatal encode errors: `error` / `MediaRecorderErrorEvent`. **S1, S2, S5** primary.

- **F3. Start/Stop as one toggle is documented; `timeslice` is optional.** Overview sample: one button Start↔Stop; after stop, blob goes to a player. `start(10000)` or `requestData()` to force chunks. Device picker via `enumerateDevices()` + `<select>` of `audioinput`. **S2, S5** primary.

- **F4. Free level meter = AnalyserNode + rAF + canvas; output may stay unconnected.** Create via `createAnalyser()`; `createMediaStreamSource(stream)` → analyser. Default `fftSize` 2048; `frequencyBinCount` = half FFT. Oscilloscope: `getByteTimeDomainData` into `Uint8Array` of length `fftSize` (not bin count), plot `v = sample/128` (128 = mid). Bars: smaller `fftSize` (demo 256) + `getByteFrequencyData`; MDN ×2.5 bar width to hide empty highs. Scale: `minDecibels`/`maxDecibels`/`smoothingTimeConstant`. **S3, S6, S8** primary.

- **F5. Clip / peak: float time-domain |x|≥1.0; byte 128 is mid, 0/255 are rails.** `getFloatTimeDomainData`: PCM “nominal range of -1.0 to 1.0, but values can exceed the range such as when down-mixing stereo to mono.” Cheap peak-hold = max |sample| per rAF frame; warn at ≥1.0. Byte API is 0–255 with `v = sample/128` (MDN oscilloscope); 128≈silence, 0/255 = visualization rails, not ITU true-peak. web.dev points raw buffers / WAV convert at `AudioWorkletProcessor.process()` if you need every sample. **S8, S9, S11** primary. Headroom (−1 dBFS) and “don’t use FFT max as VU” are industry practice, not in these pages [speculation].

- **F6. Denial is one `NotAllowedError` — settings recovery, no JS re-prompt.** HTTP, session/global deny, or missing Permissions-Policy → `NotAllowedError`. Promise may hang if the dialog is ignored. Also: `NotFoundError` (no mic), `NotReadableError` (granted but OS/hardware block), `OverconstrainedError` (`constraint` name), `AbortError`, `SecurityError`, empty constraints / `mediaDevices` undefined → `TypeError`. UA must show capturing-now *and* permission-granted-but-idle (Firefox: pulsing red vs gray URL-bar). Iframe needs `allow="microphone"`. **S7** primary. AddPipe 2017 [stale]: old Chrome aliases (`PermissionDeniedError`, `PermissionDismissedError`) — fallbacks only. **S10**.

- **F7. Dictaphone error path is only `console.error` — product must map errors to copy.** Tutorial catch: “The following getUserMedia error occurred: ${err}”. Else: “getUserMedia not supported”. No silence, clip, countdown, or max-duration UX in MDN/web.dev demos. **S5, S11** primary.

- **F8. Ask mic only when first needed; deny is permanent from JS.** web.dev (Kinlan): users “frequently block… or ignore” if context is unclear; “only ask… when first needed”; grant persists; “if they reject access, you can't ask the user for permission again.” Permissions API `query({name:'microphone'})` → `granted` / `prompt` / `denied` so UI can change *before* `getUserMedia` (Safari support = worker 08). **S11** primary [article last-updated 2016-08-23, stale examples].

- **F9. Meet: intention pre-prompt, then “Click Allow”, plus a no-mic path.** Old load-time dialog + chip + OS prompt stacked; users feared being live with no later mute; Block is hard to undo (address-bar Site settings). New: ask if they want to be heard; only then prompt; button “Allow microphone and camera”; remind mute still works; coach “Click Allow”; continue without mic. **+14%** first-join allow — mostly fewer prompts, not converting blockers. Ignore/X ≠ Block. **S12** primary.

- **F10. Progressive fallback and review: file+`capture`, or in-page MediaRecorder → Blob → `<audio>`/download.** web.dev: `<input type=file accept="audio/*" capture>` works everywhere; desktop = file picker (`capture` ignored); iOS Safari = native mic app then return; Android = choose a recorder app. In-page: `getUserMedia({audio:true, video:false})` → MediaRecorder (`audio/webm` in sample) → chunks → Blob URL → download or `<audio controls>`. Enumerate `audioinput` + `deviceId` to pick a mic. **S11** primary. Retry = Delete (Dictaphone) or discard Blob and `start()` again once `inactive`. **S5**. Max duration: no MediaRecorder property in read pages — app `setTimeout`/`stop()` (same shape as MDN canvas demo’s 9 s stop). **S2**.

- **F11. In-page chrome should duplicate UA recording indicators.** Spec/MDN: UA must show capturing-now *and* permission-granted-but-idle. Firefox: pulsing red URL-bar while recording, gray when permitted but idle. Product still needs a Record/Stop label + red chrome (Dictaphone) because users watch the page, not the chip. Stream-end = auto-stop — treat as unexpected end + recovery. **S7, S5**.

## Conflicts and uncertainty

- **When to call `getUserMedia`.** Dictaphone (S5) requests audio as soon as the script runs. web.dev (S11) + Meet (S12) say ask only when first needed / after an intention tap. Prefer S11/S12 for a recruiter demo.
- **Countdown / HireVue.** SEO blogs claim ~30 s prep, “Not Recording”, ~3 s pre-roll, 2–3 min auto-stop. Pages unread; no first-party help in budget. **Do not cite.**
- **Silence.** No primary pattern. [speculation]: near-zero float (or byte ~128) for N seconds → “We can’t hear you.”
- Dictaphone `prompt()` to name clips is review-after-stop shape only.
- AddPipe Chrome 62 names [stale]; use MDN S7.
- NN/g voice article is Alexa/Siri VUI, not clip recorders — skipped.
- Pause exists in the API; no primary says interview recorders should expose it.
- Worker 08 owns 44px / WCAG; this note is interaction + error copy only.

## Quotes

- “Recording is not occurring — it has either not been started yet, or it has been started and then stopped.” **S4**
- “Individual Blobs containing slices of the recorded media will not necessarily be individually playable.” **S2**
- “You don't need to connect the analyser's output to another node for it to work” **S6**
- “nominal range of -1.0 to 1.0, but values can exceed the range such as when down-mixing” **S9**
- “It's possible for the returned promise to neither resolve nor reject” **S7**
- “if they reject access, you can't ask the user for permission again” **S11**
- “increase the share of users who allow microphone and camera usage when first joining a call by 14%” **S12**

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder | MediaRecorder - Web APIs \| MDN | 2024-07-26 | primary | Interface + example dictaphone flow |
| S2 | https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API | MediaStream Recording API - Web APIs \| MDN | 2025-08-11 | primary | Process, pause/resume, blobs, toggle example |
| S3 | https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode | AnalyserNode - Web APIs \| MDN | 2026-08-22 | primary | Meter node + oscilloscope sample |
| S4 | https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/state | MediaRecorder: state property - MDN | 2024-02-08 | primary | Exact inactive/recording/paused defs |
| S5 | https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API | Using the MediaStream Recording API - MDN | 2025-08-12 | primary | Web Dictaphone Record/Stop/review |
| S6 | https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Visualizations_with_Web_Audio_API | Visualizations with Web Audio API - MDN | 2025-12-31 | primary | Oscilloscope + bar graph how-to |
| S7 | https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia | MediaDevices.getUserMedia() - MDN | 2025-11-30 | primary | Errors, hang, in-use indicator |
| S8 | https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/getByteTimeDomainData | AnalyserNode.getByteTimeDomainData - MDN | 2024-07-21 | primary | Byte waveform; /128 mid |
| S9 | https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/getFloatTimeDomainData | AnalyserNode.getFloatTimeDomainData - MDN | 2025-08-12 | primary | PCM ±1; can exceed |
| S10 | https://blog.addpipe.com/common-getusermedia-errors/ | Common getUserMedia() Errors - AddPipe | 2017-11-16 | secondary | Error aliases; [stale][marketing] |
| S11 | https://web.dev/articles/media-recording-audio | Recording Audio from the User - web.dev | 2016-08-23 | primary | File+capture fallback; ask-when-needed; Permissions API; [stale] date |
| S12 | https://web.dev/case-studies/google-meet-permissions-best-practices | Google Meet permissions best practices - web.dev | 2024-06-11 | primary | Pre-prompt; +14% allow; Block recovery |

## Needs-browser

- https://www.aceround.app/blog/does-hirevue-record-during-prep-time/ — SEO; countdown claims; not first-party (skipped at cap).
- https://prepclubs.com/blog/hirevue-interview-format-questions — same; 30 s / 2–3 min claims unread.
- https://www.nngroup.com/articles/voice-interaction-ux/ — Alexa/Siri; likely off-scope.

## Searched

- MDN MediaRecorder API
- MDN AnalyserNode getByteFrequencyData
- Nielsen Norman voice UI recording
- MDN MediaRecorder state pause
- getUserMedia NotAllowedError MDN
- audio clipping peak meter Web Audio
- HireVue recording countdown timer UX
- web.dev microphone permission UX

