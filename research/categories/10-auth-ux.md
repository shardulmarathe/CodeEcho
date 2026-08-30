# Category 10 — Auth / guest / progress UX

**Evidence:** [`../notes/10-auth-ux.md`](../notes/10-auth-ux.md)  
**Audience:** recruiter (often never signs in)  
**Repo gap verified:** `frontend/src/app/progress/page.tsx` redirects unsigned users to `/sign-in` even though guest attempts API exists

## Bottom line

Keep the demo **guest-first**. The polish gap is `/progress` (and `/account`) walling guests. Invite sign-in **after** a scored attempt to save history; keep email OTP; fix Supabase template/`{{ .Token }}` and respect free SMTP **2 emails/hour** [S1][S4][S5][S10].

## Key evidence

- NN/g: login walls stop users [S1]; optional login and code-in-tab without leaving the page [S2]; passwordless OTP cost tradeoffs [S7]
- Baymard: delay account creation; forced-account abandon ~**18%** on their list [S5][S6]
- Supabase: prefetch/Safe Links burn confirmation URLs → use token OTP or click-to-confirm page [S3][S4][S9]
- Magic-link pitfalls (practitioner): in-app mail WebView signs in the wrong browser [S8][secondary]
- Empty states need status + pathway; labeled sample data OK, never fake “your” scores [S11]
- Learning-analytics RCT abstract: charts-only dashboards may add cognitive load without grade lift; actionable feedback helped verification—name a weakest dimension [S12]

## Recommended CodeEcho actions

1. Let guests open `/progress` for **this-browser** history via existing `X-Guest-Token`.
2. Empty guest progress: explain what would appear + CTA to Practice (optional labeled sample).
3. After first scorecard: soft prompt “Save history with email code”—not a hard wall.
4. Confirm OTP template uses `{{ .Token }}`; copy that mentions rate limit / keep practicing as guest.
5. Do not migrate IdP; do not require account to try Practice/Interview.

## Sources (note-local)

See note `10` Sources S1–S12 (NN/g, Baymard, Supabase Auth docs, magic-link pitfalls, MIT DSpace abstract).
