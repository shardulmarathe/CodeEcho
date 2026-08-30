# 07 — Honest reliability UX for free-tier demos (cold start, 429, silent mock, STT)

**Worker:** research-worker · **Budget used:** 18/12 calls (cap 20) · **Date:** 2026-08-30

**Worker scope:** recruiter-facing honesty for wake / 429 / degraded / mock / STT. Not visual craft (06), mobile a11y (08), SEO (09), or auth (10).

## Findings

- **[S1 primary] NN/g (2023-05-14): recognize / diagnose / recover; the worst error is no message.** Heuristic 9. Visible near the source; redundant text+icon+contrast (never color-only); precise (not “An error occurred”); constructive remedy; non-blaming; severity-matched (banner/toast for “good to know”; modal only for blockers). Preserve input. Hide codes except for diagnostics. **“The very worst error messages are those that don't exist”** — no feedback after a failure “create[s] a cascade of misunderstanding.” Total-failure (overloaded servers): wait/retry later. Applies to wake, 429, mock, STT: if the recruiter cannot *recognize* a degraded path, NN/g treats that as the worst class of error.

- **[S2 primary] Render Free sleep is a named wait; the platform loading page is browser-document only.** Idle 15 min (HTTP + existing WS). Next HTTP or *new* WS: spin-up “about one minute”; “Render displays a loading page to connecting browsers.” Local FS lost on spin-down. 750 Free instance-hours/workspace/month; spun-down do not consume hours; exhaust → all Free webs suspended until next month. No card + bandwidth overage → all Free services suspended. Render may restart Free web anytime. `/robots.txt` while spun down is synthetic “disallow all” and **does not wake**. Implication: a recruiter hitting the *API* from a already-loaded SPA does **not** get Render’s loading page — the UI can look hung unless the app owns a “server waking (~1 min)” state. Official clock ~60s vs CodeEcho-measured ~31s: same class, different clocks.

- **[S3+S7+S8 primary] 429 is a distinct failure, not a 500 and not a success.** MDN (2026-06-22): 429 = too many requests in a window; `Retry-After` *may* say how long to wait; RFC 6585 §4. Example copy: “You're doing that too often! Try again later.” Stripe API [S7]: 429 = “Too many requests hit the API too quickly. We recommend an exponential backoff”; separate from 5xx (“Stripe’s end”) and from 401/403 (no key / no permission). Stripe error-handling [S8]: each error has `type`, human `message`, `code`, `param`, **request ID** (`req…`), and `request_log_url`; `RateLimitError` is its own class (“too many API calls in too short a time”). Card `message` “can be shown to your users.” Local budget OK + upstream 429 are two truths — collapsing them into a successful mock bank violates status semantics and NN/g precision.

- **[S10+S12+S13 primary] GOV.UK: banners for known service-wide limits; shutter vs unexpected-problem pages; never vague.** Notification banner [S10]: tell users about something they need to know that is *not* the page task (whole-service delay, maintenance). `role="region"` + labelled title; `role="alert"` + focus only for success. **Use sparingly — “people often miss them.”** If the fact is about *this* action, put it in the page (inset/warning), not only a banner. One banner; combine messages. Not for validation (use error summary). Neutral banner example: processing delay. Service unavailable [S12] = **on-purpose** close (aka 503/shutter): H1 “Sorry, the service is unavailable”; day/date/time of return **or** permanent close; what happened to in-progress answers; no breadcrumbs; **do not use “vague, unhelpful words like maintenance, improvements”**; no red scare-text. Problem-with-service [S13] = **unexpected** (aka 500): H1 “Sorry, there is a problem with the service”; “Try again later.”; saved-or-lost answers; **“Log all errors”**; same page for all unexpected problems; if not fixed quickly, switch to shutter. Do not use jargon “500 or bad request” or “We are experiencing technical difficulties.” Mapping: Render sleep / known free-tier wake → expected-delay banner (not a full shutter if the process is coming up). Campus/LLM 429 or revoked key → problem-with-service (or in-page copy) plus logs. Planned hour-cap suspend → shutter with a when-back if known.

- **[S4+S9 primary] `/health` 200 must not claim “the product works.”** Kubernetes [S4]: *liveness* = restart unrecoverable failure (deadlock); **wrong liveness → cascading restarts under load**. *Readiness* = accept traffic; fail → drop from endpoints. Startup probe covers long init so liveness does not kill a booting app (cold-start analog). Official note: for a **strict** backend dependency, liveness can stay process-healthy while readiness also checks that backend — “avoid directing traffic to Pods that can only respond with error messages.” Azure Health Endpoint Monitoring [S9]: HTTP 200 is “the minimum” and “supplies little information about the operations.” **Check response content even when status is 200** to catch errors that affect only a section. Expose **at least two** endpoints (core vs lower-priority); a geocoding-class dep can be down minutes while the app is still healthy. Health checks do **not** replace logs. Expensive checks can timeout and mark the app down. Traffic Manager treats **only 200** as available; any other code = offline. CodeEcho incident (green health + revoked key + mock questions) is the 200-with-wrong-content case [S9+S14].

- **[S6+S14 primary] Graceful degradation is valid only if cheaper, rare, exercised, and *counted as not-success*.** SRE Ch.22 [S6]: “Serve degraded results” = “lower-quality, cheaper-to-compute”; alternatively **fail early and cheaply** (example: HTTP 503 when too many requests in flight). Load shedding exists to avoid failing health checks / extreme latency. **“The code path you never use is the code path that (often) doesn't work.”** Degraded mode is unused in steady state → less operational experience → higher risk; exercise it on a subset near overload. **Monitor and alert when servers enter these modes.** Complexity can trip degradation when not wanted; provide a kill switch. Cold cache / slow startup [S6]: just-started processes are slower; empty caches make every request expensive — provision or protect, don’t treat first-hit slowness as a product bug. Four golden signals [S14]: latency, traffic, errors, saturation. **Errors include implicit failures: “HTTP 200 … but coupled with the wrong content.”** Protocol codes are not enough for partial failure; need a secondary/internal signal. Load-balancer 500s catch total failure; **only end-to-end tests catch wrong content.** White-box (logs/endpoints) detects **“failures masked by retries.”** Dashboards should answer basic questions and normally include the four signals. Simple monitoring over magic. For a portfolio demo, the free bar that follows these texts: (1) capability JSON or banner bits (`llm: live|mock|429`, `budget`, `stt`) so 200 is not the only signal; (2) request/correlation id on failures [S8]; (3) logs of fallback/429 (GOV.UK [S13]); (4) visible wake wait [S2+S1]; (5) do not page anyone — but do not hide implicit 200s.

- **[S11+S15 primary] STT failures are a typed enum; map `error`, do not treat `message` as UI copy.** MDN (2025-09-30) [S11]: `SpeechRecognitionErrorEvent.error` values include `no-speech`, `not-allowed` (security/privacy/user preference), `audio-capture`, `network` (recognition needs network — Chrome-class cloud STT), `aborted`, `language-not-supported` (no programmatic list of supported langs), `service-not-allowed`, `phrases-not-supported`; `bad-grammar` is leftover/no longer in the spec. Feature is **not Baseline**. MDN `message` (2023-04-08) [S15]: extra detail; **“the spec does not define the exact wording … up to the implementors.”** So UI copy must be the app’s, keyed off `error` (NN/g: plain language + remedy): e.g. `not-allowed` → type instead; `no-speech` → try again / type; `network` → STT needs a connection, type instead. Silent STT failure is again S1’s worst class.

## Conflicts and uncertainty

- K8s [S4] allows readiness to include **required** backends so traffic is not sent to error-only pods; Azure [S9] says optional deps can be down while the app stays healthy. Not a true contradiction if CodeEcho splits probes: process liveness stays green; a *capability* surface reports LLM/STT. A single boolean `/health` cannot satisfy both.
- Render official wake “about one minute” [S2] vs CodeEcho ~31s and vendor blogs 30–90s (blogs not used as primary).
- SRE [S6] endorses cheaper degraded results *and* fail-early 503; it does **not** endorse a silent mock that looks like a live LLM. Whether a *labelled* mock bank is “cheaper degraded” or “wrong content” [S14] depends on whether the response is marked. Unlabelled mock = implicit error.
- Stanford ~$3/day 429 vs local budget OK: background only; no campus quota page fetched (worker 05).
- Heuristic 1 (visibility of system status) is the usual “always show progress” cite; this worker’s ten-heuristics fetch was truncated before H1 body — do not cite H1 from this note. S1 visibility rules + S10 banners cover wake UX without it.
- Web Speech spec line that `message` must not be shown in UI was **not** fetch.py-confirmed; only MDN’s “wording is implementor-defined” [S15] is cited.
- Medium / InterviewLane 429 UX and PWA-offline blogs: leads only, not read as evidence.

## Quotes

> "The very worst error messages are those that don't exist." [S1]
> "Generic messages such as An error occurred lack context." [S1]
> "This process takes about one minute." [S2]
> "Render displays a loading page to connecting browsers while a service is spinning up." [S2]
> "A Retry-After header may be included to this response" [S3]
> "Incorrect implementation of liveness probes can lead to cascading failures." [S4]
> "Serve lower-quality, cheaper-to-compute results to the user." [S6]
> "The code path you never use is the code path that (often) doesn't work." [S6]
> "Too many requests hit the API too quickly. We recommend an exponential backoff" [S7]
> "Checking the status code is the minimum implementation of this pattern." [S9]
> "There's evidence that people often miss them" [S10]
> "vague, unhelpful words like maintenance, improvements" [S12]
> "Log all errors and fix them as quickly as possible." [S13]
> "an HTTP 200 success response, but coupled with the wrong content" [S14]
> "the spec does not define the exact wording of these messages" [S15]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/error-message-guidelines/ | Error-Message Guidelines - NN/G | 2023-05-14 | primary | Heuristic 9; visibility/copy |
| S2 | https://render.com/docs/free | Deploy for Free – Render Docs | unknown (fetched 2026-08-30) | primary | Sleep, ~1 min wake, loading page |
| S3 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429 | 429 Too Many Requests - HTTP \| MDN | 2026-06-22 | primary | Status + Retry-After |
| S4 | https://kubernetes.io/docs/concepts/workloads/pods/probes/ | Liveness, Readiness, and Startup Probes | unknown (fetched 2026-08-30) | primary | What probes must not conflate |
| S6 | https://sre.google/sre-book/addressing-cascading-failures/ | Addressing Cascading Failures \| SRE Book Ch.22 | unknown (fetched 2026-08-30) | primary | Degrade vs fail-early; unused paths |
| S7 | https://docs.stripe.com/api/errors | Errors \| Stripe API Reference | unknown (fetched 2026-08-30) | primary | HTTP map; 429 vs 5xx vs 401 |
| S8 | https://docs.stripe.com/error-handling | Error handling \| Stripe Docs | unknown (fetched 2026-08-30) | primary | type, message, request id, RateLimitError |
| S9 | https://learn.microsoft.com/en-us/azure/architecture/patterns/health-endpoint-monitoring | Health Endpoint Monitoring pattern | unknown (fetched 2026-08-30) | primary | 200 insufficient; content check |
| S10 | https://design-system.service.gov.uk/components/notification-banner/ | Notification banner – GOV.UK Design System | unknown (fetched 2026-08-30) | primary | Service-wide banner rules |
| S11 | https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionErrorEvent/error | SpeechRecognitionErrorEvent: error - MDN | 2025-09-30 | primary | STT error enum |
| S12 | https://design-system.service.gov.uk/patterns/service-unavailable-pages/ | Service unavailable pages – GOV.UK | unknown (fetched 2026-08-30) | primary | Planned 503 / shutter copy |
| S13 | https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/ | There is a problem with the service pages – GOV.UK | unknown (fetched 2026-08-30) | primary | Unexpected 500; log all errors |
| S14 | https://sre.google/sre-book/monitoring-distributed-systems/ | Monitoring Distributed Systems \| SRE Book Ch.6 | unknown (fetched 2026-08-30) | primary | Four golden signals; implicit 200 |
| S15 | https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionErrorEvent/message | SpeechRecognitionErrorEvent: message - MDN | 2023-04-08 | primary | message wording not specified |

## Needs-browser

- None. All cited URLs returned fetch.py exit 0. Stripe `error-handling?lang=node` failed in zsh glob; unquoted-path HTML `https://docs.stripe.com/error-handling` worked [S8].

## Searched

Nielsen error message guidelines, Render free instance sleep, HTTP 429 rate limit UX, health check liveness readiness, graceful degradation fail loudly, Stripe API error messages, PWA offline banner UX, SpeechRecognitionErrorEvent MDN, Azure health endpoint monitoring, GOV.UK service unavailable pages
