# Category 08 — Mobile / accessibility

**Evidence:** [`../notes/08-mobile-a11y.md`](../notes/08-mobile-a11y.md)  
**Audience:** recruiter opening resume link on ~390px phone

## Bottom line

Never call `getUserMedia` on load; prime in-page then request mic from a real tap (Chrome desktop allow ~12% without gesture vs ~30% after) [S4]. Primary controls ≥**44×44** CSS px; WCAG AA floor **24×24** [S2][S3][S8]. Scorecards: real table in labelled scroll region or honest cards; scores as text not color-only [S6].

## Key evidence

- Mic HTTPS-only; permanent deny needs site-settings recovery copy [S1][S4]
- WCAG 2.2: focus visible/unobscured, contrast 4.5:1 text / 3:1 UI, labels on icon-only controls, status live regions, don’t lock pinch-zoom [S2]
- `prefers-reduced-motion` (MDN S12) is the vestibular/MQ win; auto-play motion &gt;5s still needs an on-page pause (WCAG 2.2.2 via S2)—the MQ does not replace it [S2][S12]
- Reflow at 320 CSS px; ~390px already wider—still avoid page-level horizontal scroll [S2][S8]
- Android 48×48 dp guidance for touch; cite 44 for primary Record/Stop/Play [S8][S9]

## Recommended CodeEcho actions

1. Gate all mic prompts behind an explicit Record button click; never on homepage load.
2. Enlarge Record/Stop/Play hit targets to ≥44×44; add accessible names.
3. Live region for recording / permission denied / score ready.
4. Score chips: include numeric text, not color alone.
5. Scorecard: `role="region"` + labelled overflow table, or card layout on small screens.
6. Honor reduced-motion for Rough.js (with category 06).

## Sources (note-local)

See note `08` Sources (WCAG 2.2, web.dev permissions, MDN getUserMedia, Roselli tables, Apple/Android targets).
