# 19 — UX for showing AI cost/budget/rate-limit state

**Worker:** research-worker · **Budget used:** 21/12 calls (cap 20) · **Date:** 2026-08-30

**Worker scope:** recruiter-facing metering (remaining quota, shared vs per-user caps, 429/try-tomorrow copy). Not campus SKU pricing or multi-grader cost math (03). Note 07 owns 429-as-error vs silent-mock; this note owns *pre-failure meters* and *named ceilings*.

## Findings

- **Show remaining quota before the wall; a meter is status, not a billing page.** NN/g H1 [S1]: keep users informed through timely feedback; analog is battery remaining / unread count / next-train minutes — “A lack of information often equates to a lack of control.” When an external event or time changes state, “explain it in brief but understandable terms.” Do not silently remove capacity (wish-list items vanishing). Inventory rule: hide stock unless *low* or *zero* — then show it so users do not attempt a dead action. GitHub [S2]: emit `x-ratelimit-limit` / `remaining` / `used` / `reset` / `resource` on **every** response; prefer headers over a poll; `GET /rate_limit` exists but still costs secondary budget. Anthropic Console [S3]: Usage page charts current input/output tokens-per-minute **against the limit** (“headroom”), plus cache-hit rate — a remaining-vs-ceiling pair, not a raw spend number. Claude.ai paid [S4]: Settings → Usage **progress bars** for the 5-hour session (used + time remaining) **and** weekly limits (Opus vs other models) with reset times. Stripe [S5][S6]: no customer-facing usage UI in first-party docs; merchant gets meter alerts (alert **Name** “isn’t visible to customers”); webhook when threshold crossed. Implication for `/api/budget`: expose remaining/limit/reset on the demo surface the recruiter already sees, not only an admin dashboard.

- **Name the ceiling that actually fired; local budget ≠ org/upstream cap.** OpenAI [S7]: three independent stop conditions — (1) **configured** org/project spend (optional hard 429 `organization_spend_limit_exceeded` / `project_spend_limit_exceeded`), (2) OpenAI-**approved** monthly usage limit (`organization_usage_limit_exceeded`), (3) prepaid credits (`credit_balance_exhausted`). Spend **alerts** “do not enforce a cap”; traffic continues. Hard-limit enforcement “is not instantaneous,” so recorded spend can slightly exceed the number. Restore path is code-specific: raise/remove configured limit vs request higher approved limit vs add credits vs rate-limit guide. Anthropic [S3]: **tier spend cap** → HTTP **429** `rate_limit_error` + `enforced_spend_limit_reached`, message includes resume `YYYY-MM-DD at 00:00 UTC`; **no `retry-after`** — SDK retries fail until the month. **Self-set** org/workspace spend → HTTP **400** `invalid_request_error`, message starts “You have reached your specified API usage limits” or “…workspace API usage limits” + when access resumes. RPM/ITPM/OTPM 429 includes **which** limiter and `retry-after`. Mapping: CodeEcho local budget OK + Stanford 429 is OpenAI’s “check `error.code`” case — collapsing them into one “out of budget” or a mock success hides the live ceiling.

- **Shared caps need two sentences: this request’s bucket, and the pool it draws from.** OpenAI [S7]: org hard limit = traffic **across all projects**; project hard limit = that project only; both can apply to one request; org 429 vs project 429 are different codes. Anthropic [S3][S8]: org limits **always apply even if workspace limits add up to more**; workspace caps may only be **lower** than org; unset workspace inherits org; unused workspace tokens “are then available for other Workspaces.” Default Workspace **cannot** carry custom limits. Claude Code workspace is “the only workspace that supports **per-user** monthly spend limits”; Claude Code is “rate-limited separately” and admins can cap its **share of the organization’s limits**. GitHub [S2]: a 15k-limit app making 10k requests on your behalf **exhausts the 5k PAT budget** even though the app still has remaining — shared personal bucket, documented in prose next to the numbers. Recruiter copy that follows these texts: “Shared demo budget (all visitors today), not your personal quota” + remaining/limit + reset — never “you used too many interviews” when the pool is campus-wide.

- **429 copy that works: named limit + when it lifts + do not retry the same action.** Anthropic [S3] exact spend-cap body: “You have reached your API usage limits: your organization has crossed its monthly API usage threshold, set based on your organization's API tier. You will regain access on 2026-09-01 at 00:00 UTC.” Rate 429: which limiter + `retry-after`. GOV.UK **planned** close / known daily cap [S9]: H1 “Sorry, the service is unavailable”; give **day, date and time** it returns, or fallback “You will be able to use the service later.”; say what happened to in-progress answers; no breadcrumbs; **do not** use “vague, unhelpful words like maintenance, improvements”; no red scare-text. GOV.UK **unexpected** [S10]: H1 “Sorry, there is a problem with the service”; paragraph “Try again later.”; same page for all unexpected problems; **log all errors**; if not fixed quickly, switch to shutter [S9]; no jargon “500 or bad request”; no “We are experiencing technical difficulties.” Research on [S10] (n=5): users want **when it will be back** and how to finish the task; GOV.UK **cannot** meet “when” for unexpected faults; open question includes “if people need to know if this affects only them or other people too.” GitHub [S2]: on primary exceed, wait until `x-ratelimit-reset`; continuing to request “may result in the banning of your integration.” Token-bucket [S3] replenishes continuously — “try tomorrow” is correct for **calendar spend**, wrong for **per-minute** 429 (honor `retry-after`). Secondary GitHub limits have **no remaining meter** [S2] — those must be explained as “burst/abuse limit, not your hourly remaining.”

- **Alerts vs hard stop are different UX states; do not wait for 429 to start talking.** OpenAI [S7]: alerts fire **before** a hard limit “interrupts traffic.” Stripe [S6]: one-time per-customer threshold (example: 100 API calls) → merchant webhook; evaluation includes usage reported **before** the alert was created. NN/g [S1]: low-stock and out-of-stock are the two moments backstage inventory must come frontstage; progress indicators exist so users do not tap again. Claude [S4]: watch session + weekly bars **before** a long task. For a free recruiter demo: warn when shared remaining is low; shutter with a clock when empty; never a silent mock that looks like live grading.

## Conflicts and uncertainty

- OpenAI Help “Reviewing API usage and costs” and “ChatGPT Free Tier FAQ” returned HTTP **403** (exit 4). Consumer ChatGPT “you’ve reached our limit / try again later” copy is **unconfirmed** here (content-farm leads only). Do not cite ChatGPT in-product strings from this note.
- Anthropic **tier** spend cap = 429; **self-set** spend = 400. OpenAI configured hard spend = 429. Same user meaning (“cap hit”), different status codes — UI must key off `error.code` / `error_code`, not HTTP class alone.
- GitHub rate-limit exceed is **403 or 429**, not 429-only [S2]. MDN 429 body not re-fetched this wave (note 07).
- Stripe [S5] now steers new builds to Metronome; Billing Meters remain for existing integrations. Neither page specifies a customer-visible remaining bar.
- Anthropic Usage **progress bars** documented for Pro/Max/Team/seat Enterprise only [S4]; Free Claude detailed session % not in this primary page.
- GOV.UK [S10] research explicitly unresolved: whether users need to know if an outage is **personal vs everyone** — the shared-campus question. [unconfirmed] beyond that n=5 note.
- OpenAI Usage Dashboard lag (“~5 minutes”) appeared only in a secondary blog; not used.
- RateLimit IETF draft / `RateLimit-*` headers: blog leads only; not fetched. GitHub `x-ratelimit-*` is the primary remaining-quota pattern cited.
- OUT OF SCOPE (03): multi-grader cost math. Campus dollar SKU not fetched.

## Quotes

> "A lack of information often equates to a lack of control." [S1]
> "Don’t blindfold your users!" [S1]
> "When possible, you should use the rate limit response headers" [S2]
> "Organization-wide limits always apply, even if Workspace limits add up to more." [S3]
> "You will regain access on 2026-09-01 at 00:00 UTC." [S3]
> "progress bars showing how much of your five-hour session and weekly usage limits you’ve consumed." [S4]
> "This isn’t visible to customers." [S6]
> "Spend alerts do not enforce a cap." [S7]
> "Sorry, the service is unavailable" [S9]
> "vague, unhelpful words like maintenance, improvements" [S9]
> "Try again later." [S10]
> "if people need to know if this affects only them or other people too" [S10]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://www.nngroup.com/articles/visibility-system-status/ | Visibility of System Status - NN/G | 2018-06-03 | primary | H1; remaining-quota analogs |
| S2 | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api | Rate limits for the REST API - GitHub Docs | unknown (fetched 2026-08-30) | primary | remaining headers; shared PAT bucket |
| S3 | https://platform.claude.com/docs/en/api/rate-limits | Rate limits - Claude Platform Docs | unknown (fetched 2026-08-30) | primary | spend vs rate; 429/400 copy; org vs workspace |
| S4 | https://support.claude.com/en/articles/9797557-usage-limit-best-practices | Usage limit best practices \| Anthropic Help Center | 2026-06-02 | primary | Settings > Usage progress bars |
| S5 | https://docs.stripe.com/billing/subscriptions/usage-based | Basic usage-based billing \| Stripe Docs | unknown (fetched 2026-08-30) | primary | meters; no customer UI specified |
| S6 | https://docs.stripe.com/billing/subscriptions/usage-based/alerts | Set up usage-based alerts \| Stripe Docs | unknown (fetched 2026-08-30) | primary | merchant webhook; name hidden from customers |
| S7 | https://developers.openai.com/api/docs/guides/spend-limits | Spend limits \| OpenAI API | unknown (fetched 2026-08-30) | primary | alert vs hard 429; org vs project codes |
| S8 | https://platform.claude.com/docs/en/manage-claude/workspaces | Workspaces - Claude Platform Docs | unknown (fetched 2026-08-30) | primary | per-user spend only on Claude Code workspace |
| S9 | https://design-system.service.gov.uk/patterns/service-unavailable-pages/ | Service unavailable pages – GOV.UK | unknown (fetched 2026-08-30) | primary | planned cap / try-from-datetime copy |
| S10 | https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/ | There is a problem with the service pages – GOV.UK | unknown (fetched 2026-08-30) | primary | unexpected; “Try again later.”; shared-vs-me research gap |

## Needs-browser

- https://help.openai.com/en/articles/10478918-api-usage-dashboard — exit 4 (HTTP 403)
- https://help.openai.com/en/articles/9275245-using-chatgpt-s-free-plan — exit 4 (HTTP 403)
- https://platform.claude.com/docs/en/api/rate-limits.md — exit 3 (markdown); HTML [S3] used; header-name table truncated
- https://developers.openai.com/api/docs/guides/rate-limits.md — exit 3 (markdown); not used

## Searched

OpenAI usage dashboard limits, Stripe usage billing dashboard, rate limit remaining header UX, GitHub REST rate limit remaining, Anthropic spend limits workspace, NN/g visibility system status, Stripe billing usage alerts docs, ChatGPT rate limit reached help, Claude.ai usage page help, OpenAI help ChatGPT usage limits
