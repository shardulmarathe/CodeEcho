# Category 15 — Voice / recorder UX

**Evidence:** [`../notes/15-voice-recorder-ux.md`](../notes/15-voice-recorder-ux.md)

## Bottom line

Browser `MediaRecorder` only exposes inactive/recording/paused—**review, countdown, max duration are app states**. Ask for mic **after a tap** (Meet-style pre-prompt); recover denial via site settings; meter with `AnalyserNode`; clip warn when float samples hit ±1.0.

## Key evidence

- MDN Web Dictaphone pattern: Record → Stop → Blob → `<audio controls>` + Delete
- Free meter: AnalyserNode + rAF + canvas; clip on `getFloatTimeDomainData` |x|≥1
- Deny = NotAllowedError; cannot re-prompt from JS after block
- Meet case study: pre-prompt + “Click Allow” + no-mic path improved first-join allow rates
- Mobile fallback: `<input type="file" accept="audio/*" capture>` where useful
- Prefer intention-tap over Dictaphone’s script-load mic ask

## Recommended CodeEcho actions

1. Explicit state machine: idle → priming copy → recording → review → retry/discard.
2. Level meter + clip warning; near-zero meter as soft “no speech?” hint (inferred).
3. Max-duration timer that calls `stop()`.
4. Site-settings recovery copy on permanent deny; keep no-mic sample path (cat 12).
5. Optional: near-zero meter as a soft “no speech?” hint (**inferred**, no primary standard).

## Sources

See note `15` (MDN MediaRecorder/Web Audio, web.dev recording + Meet permissions).
