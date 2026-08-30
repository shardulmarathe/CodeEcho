# Category 27 — Design / UI spec checklist (homepage + scorecard + recorder)

**Evidence:** [`../notes/27-design-spec-synthesis.md`](../notes/27-design-spec-synthesis.md)  
**Extends:** categories 12, 15, 16  
**Note:** Markdown implementer checklist — not a Figma file. W3C APG Disclosure unread (HTTP 403).

## Bottom line

Public UX sources support: (1) homepage leads with a **real content sample** and one specific CTA — not a mic prompt (persistent “Sample” label is also cat-12 policy); (2) scorecard keeps the **score visible**, parks rubric/sources behind one-tap disclosure (≤2 levels); (3) recorder is an explicit state machine: priming → permission → recording → Blob review, with dual indicators; file-capture fallback is web.dev secondary/[stale] (2016) — still useful progressive enhancement.

## Spec checklist (implement)

### Homepage
1. Elevator pitch + who/what above the fold (NN/g homepage principles).
2. Labeled fixture sample scorecard as hero content (not stock art / category teasers).
3. Primary CTA with scent: e.g. “View a sample scorecard” — not “Get started” / “Allow microphone.”
4. At most 1–4 starting tasks; visually distinct from interior pages.

### Scorecard
5. Score + one-line rationale always visible.
6. “How this was graded” as one Details (or accordion for peer dimensions); disclosure labels have scent.
7. Cap depth at two levels; omit empty Sources row rather than blank chips.
8. Do not hide text most users need behind Details (GOV.UK).

### Recorder
9. States: `idle` → `priming` → `awaiting_permission` → `recording` | `denied` | `unavailable` → `review` → `retry` | `discard`.
10. Intention tap before `getUserMedia`; priming explains why mic / what is stored / Cancel.
11. Map `NotAllowedError` / `NotFoundError` / `NotReadableError` to recovery copy (no useless re-prompt).
12. In-app Recording + elapsed time (not color-only); dual OS indicators acknowledged.
13. Review = assembled Blob → `<audio controls>` + discard; fallback `<input type="file" accept="audio/*" capture>`.

### Craft
14. Keep Rough.js off the critical path of labels; keyword-first button names.

## Recommended CodeEcho actions

1. Implement homepage sample + CTA before polish on mic-first flows (aligns 00c #1 and cat 23 wedge).
2. Scorecard Details for rubric/sources after score chrome (cat 16).
3. Recorder state machine before level-meter cosmetics (cat 15).

## Sources

See note `27` (S1–S10 used; S11–S13 failed/unused).
