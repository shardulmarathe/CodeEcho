# Category 06 — UI / visual craft / motion

**Evidence:** [`../notes/06-ui-craft.md`](../notes/06-ui-craft.md)  
**Audience:** recruiter / portfolio (A) · **Constraints:** free tier, keep Rough.js sketch system

## Bottom line

Keep the sketch aesthetic. Credibility in the first glance comes from a **plain-language hero** (what this is / who it’s for) [S4], plus **obvious voice-state feedback** [S1] and a **tiny purpose-bound motion scale** with reduced-motion fallbacks [S5][S8]—not a generic SaaS restyle.

## Key evidence

- One ex-recruiter/PD account: first ~10s is a **match** screen (role/what-this-is), not a Figma critique; unfinished craft and sameness still hurt later readers [S4][opinion]
- Aesthetic-usability: orderly UI raises *perceived* usability but only forgives minor issues [S2][S3]
- Nielsen #1 status visibility + #8 minimalist design: recording/listening/scoring chrome is the craft demo [S1]
- Motion needs a named goal, user cause, start within ~0.1s; avoid scroll fade-ups and looping noise [S8]
- Feedback &lt;400ms (Doherty); purposeful delay only when it communicates value (e.g. scoring) [S7]
- `prefers-reduced-motion`: opacity not scale/pan; JS/Rough/WAAPI need `matchMedia` (CSS alone won’t stop canvas) [S5][S6]
- Rough.js as intentional anti-generic system—tokenize roughness/bowing so it reads finished [S9]

## Recommended CodeEcho actions

1. Hero: one sentence job-in-English above the fold (SWE interview prep you speak aloud).
2. CSS tokens `--motion-micro: 100ms` / `--motion-status: ~300ms` only where a goal is answerable (mic state, scoring progress).
3. Wire reduced-motion for CSS **and** Rough.js/canvas.
4. Zero decorative scroll fade-ups; avoid generic/sameness restyles that erase the sketch system [S4][S1].

## Sources (note-local)

See note `06` Sources S1–S9 (NN/g, Laws of UX, Rough.js, MDN/web.dev).
