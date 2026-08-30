# 13 — Free-tier cold start and perceived performance (Render sleep + loaded SPA)

**Worker:** research-worker · **Budget used:** 19/12 calls (cap 20) · **Date:** 2026-08-30

**Worker scope:** Render/Vercel/Supabase free sleep/hours/keepalive; perceived-performance during wake (skeleton, optimistic UI, progress); anti-patterns (fake-ready, ping-to-750h). Not error-banner copy (07), SEO (09), competitive (14).

## Findings

- **[S1 primary] Render Free web: 15 min idle → spin-down; wake “about one minute”; 750 instance-hours/workspace/calendar month.** Idle = no inbound HTTP and no WebSocket messages on existing connections. Next HTTP or *new* WS starts spin-up. Official clock: “about one minute.” Render shows a loading page to “connecting browsers” — an already-loaded SPA’s `fetch`/XHR does **not** get that page; the UI can look hung unless the app owns a wake state. Spun-down services do **not** consume hours; running ones do. Exhaust 750h → **all** Free webs in the workspace suspend until next month; leftover hours do not roll over. `/robots.txt` while down is synthetic disallow-all and **does not wake**. Ephemeral FS lost on spin-down. Render may restart Free webs anytime. Docs: do not use Free for production. **Hour math from S1 only:** 24×30=720h; 24×31=744h; 750÷24=31.25 days of continuous run for **one** instance. One always-on Free web uses ~720–744 of 750 (slack ~6–30h). Two always-on Free webs exhaust in 750÷48≈15.6 days. A keep-warm ping every <15 min prevents sleep, so the instance stays *running* and bills **wall-clock hours**, not ping-count. Ping interval does not make always-on cheap.

- **[S1 primary] Render documents no ping ban; it does document two cost/risk limits.** Inbound HTTP is what resets the idle timer (so health pings work by definition). Separate: Render *may* suspend a Free web that “initiates an uncommonly high volume of traffic over the public internet” (outbound: external DBs/APIs/object storage). [S12] Render Terms grep for abuse/automated/keepalive/fair-use found only payment-card “abuse prevention,” not a keepalive clause. [unconfirmed] a hidden AUP — `render.com/docs/acceptable-use` is 404.

- **[S2+S3+S8 primary] Vercel Hobby is not a 15-minute instance-sleep product.** Hobby docs list 4 CPU-hrs, 360 GB-hrs, 1M function invocations, 300s function max duration (not configurable above 300s). Exceed most limits → wait ~30 days. Fair use [S3]: SPAs and “Functions that query DBs or APIs” are fair use; proxies/VPNs/scrapers/crypto/unauthorized load or pentest are not; “Circumventing or otherwise misusing Vercel’s limits” is a violation; Hobby is non-commercial personal use only. Cron [S8]: 100 jobs/project but Hobby **minimum interval once per day**; hourly/`*/30` expressions **fail deploy**; timing ±59 min inside the hour. Vercel Hobby cron **cannot** implement a 14-min Render keep-warm. Neither Hobby nor the duration table describes Render-style idle spin-down.

- **[S4+S9 primary] Supabase Free pause is ~7 days of low DB activity, not 15 minutes.** Inactive = insufficient user database activity over the past week; “Typically a few user requests to the database each day over the previous week is enough.” Warning email ~1 week before pause; confirmation after. After warning: Dashboard visit or API/app requests. Official “prevent future automatic pausing” = upgrade to Pro. Restore from Studio up to 1 year. Cron module [S9]: Jobs may run SQL **or make an HTTP request** (e.g. Edge Function); cadence from every second to yearly; recommend ≤8 concurrent jobs; each job ≤10 min. So pg_cron→Render HTTP is an **official Cron capability**, but it is **overkill for Supabase pause** (daily DB hits suffice) and **expensive for Render** (sub-15-min hits keep the web running → ~720–744h). Official pause prevention is Pro, not cron.

- **[S5+S6 primary] Nielsen thresholds, not 400ms, govern wake chrome.** 1993/2014 [S5]: **0.1s** = instantaneous, no extra feedback beyond the result; **1.0s** = flow stays; 0.1–1.0s usually no special indicator (user still notices); **>1s** = show the system is working (e.g. cursor). **10s** = attention limit; longer delays need feedback of *when* it will finish; users will do other tasks. 2014 addendum: >10s needs a **percent-done** indicator **and** a clearly signposted **interrupt**; users must reorient after >10s; >10s only OK at natural task breaks. 2014 progress article [S6]: give **immediate** visual ack on the initiating click (button pressed / page begins to change) or users retry; use a progress indicator for actions **>~1s**; **looped** spinners/bars only for **2–10s**; do **not** use looped animation for >10s (users cannot tell working vs stuck; one test user waited 15 min on a stuck spinner). >10s: estimate finish time or users “will go out for lunch.” If duration unknown, still give running work feedback (named steps), not a silent hang. NN/g reports a Nebraska-Lincoln study: looping progress bar → higher satisfaction and **~3× longer** willingness to wait vs no indicator — [secondary] via S6; original study not read. **Render ~60s (official) / ~31s (measured) is above the 10s line:** skeleton or spinner **alone** is the wrong pattern; need named wait + duration class (“about a minute”) + cancel/leave + something that changes so it does not look frozen.

- **[S7 primary] Skeleton screens are for full-page loads **under 10s**, not for a 1-minute API wake.** NN/G 2023-06-04: skeletons = wireframe placeholders for **full-page** loads; they reduce perceived wait by showing structure. Use **<10s**; **<1s** → skip (flash is annoying). Spinners: single module, 2–10s. **>10s → progress bars + explicit duration estimate**, not skeleton-as-progress. Do **not** use frame-only skeletons (header/footer/blank) — users assume the page is broken. Shimmer/pulse can distract or harm a11y. Skeletons do not replace making it faster. For a loaded SPA waiting on a sleeping API: a skeleton of interview chrome is OK **only if** paired with an honest >10s progress/time-estimate; a skeleton that implies “content is seconds away” while the origin is cold is a readiness lie.

- **[S10+S5 primary] Optimistic UI is for reversible local assumption during an in-flight Action — not “the backend is ready.”** React `useOptimistic` [S10]: show a **temporary** value while an Action is pending; it equals the real `value` when no Action is pending; official examples are like/subscribe, list add, delete **with error recovery**. It does not authorize marking the interview/API ready before the sleeping origin answers. Immediate **ack** of the click (S6) is required; optimistic **completion** of a 30–60s wake is the fake-ready anti-pattern.

- **[S11 primary] Health ≠ ready; SPA loaded ≠ API ready.** K8s: **liveness** = restart unrecoverable failure (wrong liveness → cascading restarts); **readiness** = accept traffic (fail → drop from endpoints); **startup** = long init so liveness does not kill a booting app (cold-start analog). For a **strict** backend dependency: liveness can stay process-healthy while readiness also checks that backend — “avoid directing traffic to Pods that can only respond with error messages.” `httpGet` success = HTTP 200–399; `tcpSocket` success = port open (**even if the peer closes immediately**). Analog for CodeEcho: Render accepting a connection / first byte / SPA `200` is not product-ready. Do not flip UI to “ready” on TCP, on a process `/health` that does not exercise the interview path, or because the static host is warm.

- **[S13 secondary reprint] Doherty/Thadani 1982 is sub-second *completion* productivity, not a 400ms progress-indicator spec.** Elliott hosts the Nov 1982 IBM brief GE20-0752-0: old 2s target was wrong; SRT increases disrupt a short-term action sequence; Thadhani example: **3.0s → ~180 tx/h vs 0.3s → ~371 tx/h (+106%)**. NIH: design 0.5s for 80% of tx; at 4s average SRT, task time 32→48 min. Text I read says **“sub-second”** and **0.3s / 0.5s**; it does **not** contain the string “400 milliseconds.” Laws of UX [S14 secondary] attributes “<400ms” / “not 2,000” to that paper and tells designers to “provide system feedback within 400 ms.” Treat 400ms as a popularized takeaway, not a number I verified in the IBM text. For a ~60s wake, Doherty completion is impossible; the applicable primaries are Nielsen 1s/10s [S5+S6].

- **Anti-patterns (from the above, not extra sources).** (1) Fake ready: hide wake, show interview chrome as live, or treat `/health` 200 / SPA load as readiness [S11+S7+S10]. (2) Burn the 750h: sub-15-min ping/pg_cron to stay up 24/7 ≈ one Free web’s entire month [S1+S9]. (3) Vercel Hobby cron every 14 min — deploy is rejected [S8]. (4) Looped spinner for ~60s with no duration or cancel [S6]. (5) Skeleton-only for a >10s origin wait [S7]. (6) Optimistic “session started / Q1 ready” before the API responds [S10]. (7) Always-on second Free web in the same workspace [S1]. Streaming from a sleeping Render origin is not documented as possible; client-side progressive chrome is the substitute (no streaming spec read).

## Conflicts and uncertainty

- Official Render wake “about one minute” [S1] vs CodeEcho-measured ~31s (background) vs vendor blogs 30–90s (not used). Same class; different clocks.
- **400ms:** Laws of UX [S14] vs IBM reprint text [S13] (sub-second / 0.3s / 0.5s; no “400 ms”). Do not blend.
- Keepalive “legal”: inferred from S1 idle-timer + missing ToS ban [S12], not an explicit grant. Outbound flood *can* suspend [S1].
- Supabase: official prevent-pause = Pro [S4]; Cron HTTP exists [S9]; blogs that say “cron = supported keep-alive” overread S4.
- Nebraska 3× wait [S6] is NN/g’s report of a study; paper not fetched.
- Mejtoft et al. 2018 (ACM ECCE) is cited by S7; paper body not read — do not cite their spinner-vs-skeleton significance claim from this note.
- Vercel Fluid/cold-start milliseconds: not on the Hobby/duration pages read; do not invent a Vercel sleep number.
- Render ToS was only grepped, not fully read [S12].

## Quotes

> "This process takes about one minute." [S1]
> "Render displays a loading page to connecting browsers while a service is spinning up." [S1]
> "spun-down services don't consume Free instance hours" [S1]
> "Hobby accounts are limited to cron jobs that run once per day." [S8]
> "Typically a few user requests to the database each day over the previous week is enough" [S4]
> "10 seconds is about the limit for keeping the user's attention focused on the dialogue." [S5]
> "Anything slower than 10 seconds needs a percent-done indicator" [S5]
> "we don’t recommend looped animation for actions that take longer than 10 seconds" [S6]
> "skeleton screens should be used with a wait time that’s under 10 seconds" [S7]
> "avoid directing traffic to Pods that can only respond with error messages." [S11]
> "productivity increases in more than direct proportion to a decrease in response time." [S13]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://render.com/docs/free | Deploy for Free – Render Docs | unknown (fetched 2026-08-30) | primary | 15 min, ~1 min, 750h, loading page, outbound suspend |
| S2 | https://vercel.com/docs/plans/hobby | Vercel Hobby Plan | last updated 2026-08-11 (fetched 2026-08-30) | primary | CPU/mem/invocations; 300s max duration |
| S3 | https://vercel.com/docs/limits/fair-use-guidelines | Fair Use Guidelines | last updated 2026-07-29 (fetched 2026-08-30) | primary | Fair use; no circumvent; Hobby non-commercial |
| S4 | https://supabase.com/docs/guides/platform/free-project-pausing | Project Pausing \| Supabase Docs | 2026-08-28 | primary | 7-day low activity; Pro to prevent |
| S5 | https://www.nngroup.com/articles/response-times-3-important-limits/ | Response Times: The 3 Important Limits | 1993-01-01 (2014 addendum) | primary | 0.1 / 1 / 10s; percent-done + interrupt |
| S6 | https://www.nngroup.com/articles/progress-indicators/ | Progress Indicators Make a Slow System Less Insufferable | 2014-10-26 | primary | Immediate ack; spinner 2–10s; >10s estimate |
| S7 | https://www.nngroup.com/articles/skeleton-screens/ | Skeleton Screens 101 | 2023-06-04 | primary | Skeleton <10s full-page; not frame-only |
| S8 | https://vercel.com/docs/cron-jobs/usage-and-pricing | Usage & Pricing for Cron Jobs | last updated 2026-07-15 (fetched 2026-08-30) | primary | Hobby cron once/day |
| S9 | https://supabase.com/docs/guides/cron | Cron \| Supabase Docs | 2026-08-28 | primary | HTTP jobs; every-second capable |
| S10 | https://react.dev/reference/react/useOptimistic | useOptimistic – React | unknown (fetched 2026-08-30) | primary | Temporary optimistic state; revert |
| S11 | https://kubernetes.io/docs/concepts/workloads/pods/probes/ | Liveness, Readiness, and Startup Probes | unknown (fetched 2026-08-30) | primary | Ready ≠ live; TCP-open ≠ ready |
| S12 | https://render.com/terms | Render Terms of Service | unknown (fetched 2026-08-30) | primary | Grep only; no keepalive clause found |
| S13 | https://jlelliotton.blogspot.com/p/the-economic-value-of-rapid-response.html | The Economic Value of Rapid Response Time (reprint) | 1982-11 (reprint undated) | secondary | IBM GE20-0752-0 text; not ibm.com |
| S14 | https://lawsofux.com/doherty-threshold/ | Doherty Threshold \| Laws of UX | unknown (fetched 2026-08-30) | secondary | Popularizes 400ms; not in S13 text |

## Needs-browser

- https://supabase.com/docs/guides/database/extensions/pg_cron — fetch.py exit 2 (thin; redirects to Cron docs). S9 covers the replacement URL.
- Render Terms full body — grepped only [S12]; lead may sweep if a hidden AUP is needed.

## Searched

Render free sleep, Vercel Hobby limits, Supabase free plan, Nielsen response times, skeleton screen research, Supabase pause inactivity, Doherty threshold 400ms, Vercel function duration, Vercel cron Hobby, optimistic UI Nielsen, Doherty Thadani IBM 1982
