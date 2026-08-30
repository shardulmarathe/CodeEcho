# 10 — Auth / guest / magic-link / progress UX for recruiter-demo trust

**Worker:** research-worker · **Budget used:** 18/12 (cap 20) · **Date:** 2026-08-30

**Recommendation:** Keep Audience A (recruiter, one visit, often never signs in) on a **guest-first** path. Do not wall `/practice` or the live demo. The polish gap is `/progress` (and `/account`) `router.replace("/sign-in")` when `!me.authenticated` — Nav Progress is a login wall. Backend `GET /api/attempts` already lists by `X-Guest-Token`. Push sign-in **after** a scored attempt (Baymard “confirmation step”), as optional save via existing `claimGuestAttempts`. Keep OTP-in-tab; fix the **email template** and **built-in SMTP 2/hour** — not a new IdP.

## CodeEcho mapping (repo)

- Routes: `/`, `/interview`, `/practice`, `/progress`, `/sign-in`, `/account`; `/auth/callback` exchanges `code` or maps `otp_expired` / `exchange_failed` / `missing_code`.
- Auth: `signInWithOtp` + `verifyOtp` type `email`; optional Google; guest UUID in `localStorage` (`codeecho_guest_token`) as `X-Guest-Token`.
- `/sign-in` already OTP-first + “Ignore any link” + prefetch-error copy. `/progress` UI (weakest dim, sparklines, ranking, recent) is signed-in-only.

## Findings

- **F1. No login wall until benefit is obvious (NN/g).** Walls have high interaction cost; OK for email/banking; “nuisance on sites people visit only rarely.” If benefits are not evident, drop the wall or delay until users “know exactly what to expect.” Recruiter = rare visitor. **S1** primary, 2014 [stale] examples; principle restated **S2** 2017.

- **F2. Guest must be first-class, not buried.** NN/g: Yelp hid skip-login under two layers — testers assumed an account was required. Guest checkout + password **after** the task (reciprocity). **S1**. CodeEcho: Progress in Nav → sign-in is that buried wall.

- **F3. Optional login; max features without it.** NN/g mobile: think twice before register/login; guest as escape hatch. Explain account **benefits**; Google OK as faster path; minimum fields. Do **not** confirm via email link if avoidable — app-switch disorients; prefer a **code** without leaving the page. **S2**.

- **F4. Baymard: delay account until after the “order.”** Requiring or even **nudging** account first (e.g. “New Customer” above guest) adds password/birthdate fields and abandons some users. Better: guest through the task, then 1–2 fields at confirmation; tell users up front they can save later. **84%** of sites fail to delay. **S5** primary, 2024-06-26.

- **F5. Forced account is a top *fixable* abandon reason — 18%, not 19%.** Baymard list (50-study avg cart abandon **70.22%**): among non-browse reasons, extra costs 40%, slow delivery 20%, card-trust **19%**, **“The site wanted me to create an account” 18%**, long checkout 17%. **S6** primary (browser). Aggregators often swap 18/19. Analogue: gating history behind signup is the same class of friction.

- **F6. Passwordless OTP still costs wait, inbox, spam.** NN/g 2023: OTP avoids password create/recall/type; costs include **wait for delivery** (worse on poor connectivity), then access+enter. Email is harder than SMS (must switch apps; spam risk). Magic link is the email form of OTP. Offer later password/biometrics if wanted — **do not force**. Desktop: email paste is easier than SMS. **S7** primary. CodeEcho has no SMS on free stack — stay email OTP + Google.

- **F7. Supabase: one API; template chooses Magic Link vs 6-digit OTP.** `signInWithOtp` sends Magic Link by default; OTP if `{{ .Token }}` in template. OTP = six digits. Default **1 request / 60s / user**, expire **1 hour** (OTP expiry also governs Magic Links). Auto-signup unless `shouldCreateUser: false`. Success: `user`/`session` null — tell user to check inbox. **S3**.

- **F8. Prefetch / scanners burn single-use links — OTP or click-to-confirm.** Safe Links etc. GET `{{ .ConfirmationURL }}` → “Token has expired or is invalid.” Official options: (1) `{{ .Token }}` + `verifyOtp`; (2) your-domain page + button holding the real URL. Disable **email tracking** on custom SMTP (rewrites links). Same advice on prod checklist. **S4, S9**. Default dashboard template is **link-only**. CodeEcho UI already OTP-first; residual risk is a live template that still emits ConfirmationURL. [unconfirmed] without dashboard read.

- **F9. In-app mail browsers log in the wrong tab.** GET-on-click signs in Gmail/Outlook’s WebView, not the recruiter’s Safari/Chrome tab. Mitigations: confirm-button (no GET consume); or **6-digit code in the original tab** (CodeEcho). Author flags 6-digit entropy as low-stakes only — fits practice scores, not banking. **S8** secondary (practitioner). Prod checklist: raise OTP length if more entropy needed; keep expiry ≤1h. **S9**.

- **F10. Free built-in SMTP: 2 auth emails / hour, project-wide.** Unchangeable without custom SMTP. `/auth/v1/otp` also **60s** same-user. Custom SMTP: emails from a trusted (preferably app) domain; default custom-SMTP cap **30 new users/hour**. **S10, S9**. Recruiter who *does* try Sign in after another visitor burned the bucket sees 429 — looks broken. Auth-error copy (not worker 07 banners): “Inbox delay / quota; keep practicing as guest.”

- **F11. `/progress` should work for guests; empty states must name status + next action.** NN/g: blank containers cut confidence; say **what would appear** and **how to fill**; link the key task. Loggly empty state offered **demo data** for safe exploration. Do not flash “no records” while loading. **S11**. CodeEcho signed-in empty (“Nothing here yet” + Practice) already matches. Guest wall fails F1–F5. Guest **with** attempts: show the same weakest-dim / trends / ranking / recent (API already can); chip “This browser · sign in to keep history.” Guest **empty**: same empty + optional **labeled sample** (not the visitor’s scores). Post-score: “Save this history” → `/sign-in` (Baymard confirmation analogue). `/account` can stay signed-in-only (profile), unlike Progress.

- **F12. Charts without interpretation are not “real product.”** MIT DSpace abstract (Borrella & Ponce-Cueto, Appl. Sci. 2025): RCT **n=8745**; LAD + indicators only vs + ARCS actionable feedback vs control. Feedback LAD raised **verification** (paid cert); mixed engagement; **no grade effect**. Dashboards without interpretive support can add cognitive load. **S12** primary abstract (MDPI HTML 403; PDF exit 3). CodeEcho already names weakest **content** dimension — keep that for both identities; do not add peer leaderboards (authors warn social comparison).

## Conflicts and uncertainty

- **18% vs 19% vs 24–26% forced-account:** S6 first-party list = **18%** account, **19%** card-trust. Blogs often invert or cite older 24/26. Do not use 19% for accounts.
- **OTP hourly cap:** S10 table = **30 OTPs/hour** on `/auth/v1/otp`; S9 prod checklist = **360 OTPs/hour**. Email **2/hour** built-in is consistent. Record both OTP figures.
- Live Magic Link template contents [unconfirmed].
- S1 2014 / S2 2017; S7 2023 is the current NN/g passwordless piece.
- Ecommerce → demo is analogical; no recruiter-portfolio RCT found. Demo-vendor “ungated 66%” pages unread as [marketing].
- Worker 07 owns general honesty; auth 429 / prefetch / “guest vs saved” labels are in scope here.
- Visual motion is worker 06; SEO is 09.

## Quotes

> "if there is the slimmest chance that those benefits are not evident, forego the login wall" [S1]
> "login or registration should be optional and as many features as possible should be available without logging in." [S2]
> "Do not ask users to confirm their registration through email." [S2]
> "delaying the option to create an account until the Confirmation Step is a better-performing strategy." [S5]
> "18% The site wanted me to create an account" [S6]
> "accessing the OTP is more difficult when the link is sent through email." [S7]
> "the {{ .ConfirmationURL }} sent will be consumed instantly" [S4]
> "2 emails per hour with the built-in email provider." [S10]
> "Tell the user what could be displayed, and how to populate the area with that content." [S11]
> "dashboards that lack interpretive support may impose cognitive burdens without improving outcomes." [S12]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/login-walls/ | Login Walls Stop Users in Their Tracks — NN/g | 2014-03-02 | primary | Budiu; reciprocity |
| S2 | https://www.nngroup.com/articles/checklist-registration-login/ | Checklist for Registration and Login on Mobile — NN/g | 2017-06-04 | primary | Optional login; code > email confirm |
| S3 | https://supabase.com/docs/guides/auth/auth-email-passwordless | Passwordless email logins — Supabase | 2026-08-28 | primary | Magic Link vs OTP; 60s / 1h |
| S4 | https://supabase.com/docs/guides/auth/auth-email-templates | Email Templates — Supabase | 2026-08-28 | primary | Prefetch; `{{ .Token }}`; tracking |
| S5 | https://baymard.com/blog/checkout-flow-average-form-fields | Checkout Optimization: Minimize Form Fields — Baymard | 2024-06-26 | primary | Delay account; 84% don’t |
| S6 | https://baymard.com/lists/cart-abandonment-rate | 50 Cart Abandonment Rate Statistics 2026 — Baymard | unknown (title 2026; browser) | primary | 70.22%; account **18%** |
| S7 | https://www.nngroup.com/articles/passwordless-accounts/ | Passwordless Accounts: OTPs and Passkeys — NN/g | 2023-06-25 | primary | Email OTP cost; don’t force password |
| S8 | https://etodd.io/2026/03/22/magic-link-pitfalls/ | Magic Link Pitfalls — Evan Todd | 2026-03-22 | secondary | Prefetch GET; in-app browser |
| S9 | https://supabase.com/docs/guides/deployment/going-into-prod | Production Checklist — Supabase | 2026-08-28 | primary | Custom SMTP; link scanners; OTP expiry |
| S10 | https://supabase.com/docs/guides/auth/rate-limits | Rate limits — Supabase Auth | 2026-08-28 | primary | Built-in **2 emails/h**; OTP 30/h here |
| S11 | https://www.nngroup.com/articles/empty-state-interface-design/ | Designing Empty States — NN/g | 2021-09-19 | primary | Status + cues + pathway; demo data |
| S12 | https://dspace.mit.edu/handle/1721.1/163967 | LAD RCT abstract — Borrella & Ponce-Cueto | 2025-10-27 | primary | n=8745; feedback vs charts-only |

## Needs-browser

- https://baymard.com/lists/cart-abandonment-rate — fetch.py exit 2; **swept** (S6).
- https://baymard.com/blog/ecommerce-checkout-usability-report-and-benchmark — exit 2; swept; chart not in text (reasons live on S6).
- https://www.mdpi.com/2076-3417/15/21/11493 — fetch.py exit 4 (403); PDF on DSpace exit 3. Abstract used as S12. Lead may fetch `https://dspace.mit.edu/bitstream/handle/1721.1/163967/applsci-15-11493.pdf` for effect sizes.

## Searched

Supabase passwordless email magic link, Nielsen Norman login walls, Baymard guest checkout conversion, magic link email prefetch iOS, Baymard create account abandonment, don't gate demo signup, Nielsen Norman learning dashboard progress, site:baymard.com create an account, Supabase auth rate limits email, Baymard reasons cart abandonment 2026, Nielsen Norman empty states, learning analytics dashboard MOOC RCT COPES
