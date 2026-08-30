# Note — Privacy-safe free-tier product analytics (recruiter portfolio demo)

**Worker:** 26 · **Date:** 2026-08-30 · **Scope:** Event taxonomy + $0 tools + what never to log for an audio/STT interview-prep demo. Aligns with note 18. [not legal advice]. Not implementation.

**Recommendation (evidence-weighted):** [not legal advice] On a Next.js Hobby deploy, use **Vercel Web Analytics page views only** (cookieless daily request-hash; 50k events/mo; **no custom events on Hobby**). Encode the recruiter funnel as **distinct paths** (`/`, `/practice`, `/score`, `/share`) so CTA/score/share are page views. `beforeSend`: drop events with tokens/PII in the URL; offer a simple opt-out. Do **not** send transcript, audio, signed URLs, guest tokens, or emails. Disable session replay / heatmaps / `identify` everywhere. If you need named custom events at $0, PostHog Cloud (1M events, no card, ingestion stops at free) **or** Plausible CE / Umami self-host — but replay and per-person profiles fail the ICO “statistical purposes” exception. GA4 not verified as exemption-fit this pass. Name the processor; inform + free object (ICO/CNIL).

## Findings

- **F1. Vercel Web Analytics (Hobby = $0 page views; custom events are paid).** Available on all plans. No cookies; visitor = hash of incoming request, reset daily; session lifespan discarded after 24h; no cross-site / cross-day tracking; data used as aggregates. Stored fields include timestamp, URL, dynamic path, referrer, filtered query, geo (city), OS, browser, device type. **Hobby:** 50k events/mo (page views + custom, shared across projects), 1-month reporting window, **custom events not included**. Over limit: notify, 3-day grace, then pause; Hobby cannot buy more; resume after 7 days or upgrade Pro. Pro: custom events + 2 properties; `$0.03/1k` events (no included events on Pro table). Docs tell you to `beforeSend` redact user IDs/tokens/order IDs and never put emails in custom events; returning `null` drops the event; example opt-out via `localStorage` `va-disable`. **S1, S2, S3, S4** primary [vendor].

- **F2. CNIL (FR) audience-measurement exemption (updated 4 Jul 2025).** Cookies/traceurs for audience can skip consent (Art. 82 LIL) only if: purpose **strictly** audience of *this* site (performance, nav bugs, technical/ergonomic opt, capacity, content analysis) **for the publisher only**; output **anonymous stats only**. Must **not** join with other processing or send non-anonymous data to third parties; must **not** cross-site/cross-app ID (same ID on a third-party domain = out). Recommend: inform (e.g. privacy policy); tracer life ≤ **13 months**, not auto-extended; keep collected info ≤ **25 months**; review those clocks. Vendors who **reuse data for their own account** are outside the exemption unless configured off. Non-EU transfers: check. Self-assessment tool for vendors; **not** a CNIL “certification.” Publisher must ask the vendor for config proof. **S5** primary. [not legal advice]

- **F3. ICO (UK PECR, post-DUAA) “statistical purposes” exception.** Storage/access without consent if sole purpose is aggregate stats **about how the service is used**, to **improve the service** (not who the people are). Must give **clear information** + **simple, free means to object**; if they object, stop. Allowed examples: visits by page; interactions (scroll depth, hits); device/browser/OS; how they arrived (referrer/campaign); **A/B tests**; coarse geo (city/region) that does not identify; load speed / bounce / exit. **Not** allowed without consent: logs or **recordings of individual visitors and their actions** (except security); ad measurement; connecting a visitor ID to conversions for ad partners; **tracking/profiling** individuals or categories; cross-service browsing. Third-party analytics OK only as a **processor** who only helps *you* improve *your* site, does not link to other datasets; you must tell users the third party exists. Individual-level data only as long as needed to aggregate. **S6** primary. [not legal advice]

- **F4. Plausible Cloud: cookieless daily hash; EU host; Cloud is not $0. CE is $0 software.** Official data policy: no cookies, cache, or localStorage; no persistent IDs; store page path (query dropped except `ref`/`utm_*`), referrer, derived browser/OS/device, geo from IP; **raw IP and UA never stored**; unique = `hash(daily_salt + domain + ip + ua)`, salt rotated/deleted 24h. Legal entity Estonia; visitor data on EU-owned infra, “does not leave the EU.” Account/site delete = permanent. Claims no cookie banner needed — **vendor legal opinion**, not a regulator letter. **CE:** AGPLv3, self-host, no fees to Plausible; you pay infra; fewer premium features (funnels/journeys/ecommerce/SSO/sites API listed as Cloud-only); community support; you pick hosting country (can be non-GDPR). Cloud = paid subscription (pricing URL 404 this pass; site pushes “free trial”). **S7, S8** primary [vendor][marketing on “no consent”].

- **F5. PostHog Cloud: large free event bucket; $0 if you stay in limits; replay is the privacy trap.** Official pricing: no card; **1M analytics events/mo**, 5k session recordings, 1-year retention, 1 project; “usage stops at the free tier limits, so you can’t be charged by surprise.” Replay privacy docs: **inputs masked by default**; **general page text is not masked by default** — transcript/score copy in the DOM would be sent unless `maskTextSelector: "*"` / `ph-no-capture`. Masking is client-side. ICO F3 forbids individual visit recordings for the analytics exemption. For an STT demo: **do not enable session replay** (also skip Umami v3 replay/heatmaps — S9). Hosting/transfer region not read this pass. **S9, S10** primary [vendor].

- **F6. Umami: cookieless claim; self-host or Cloud; v3 adds replay/heatmaps.** Docs: no cookies, no cross-site tracking, no automatic personal-data collection; Cloud (“create a free account”) or self-host. v3 feature list includes custom events, journeys, **session replays**, heatmaps, funnels, goals, `identify` / Distinct IDs (cross-session link). Metric defs (search lead; body not re-fetched): session hash + monthly rotating salt; IP used for geo, “never stored.” Cloud **pricing page JS-walled** (fetch exit 2). Self-host is the documented $0-to-vendor path (your Postgres/host is not $0 unless already owned). Distinct IDs / replay collide with F3 if used. **S11** primary [vendor]; pricing **Needs-browser**.

- **F7. No interview-prep-specific event standard found.** Regulator-allowed **aggregate** actions (F3) + Vercel’s own examples (`Signup`, `Purchase` + small properties) imply a **route + object-action** set, not a named industry taxonomy. Amplitude/Segment methodology pages **not read** (batch died after Vercel limits). Proposed **Hobby-safe funnel (paths, not `track()`):** `page_view /` (resume land) → `/practice` or `/demo` (CTA destination) → `/score` (results) → `/share` (optional). If a paid/custom-event tool is used, names only, no content: `cta_clicked` `{slot: hero|footer, dest: practice}`; `mic_permission` `{result: granted|denied|unavailable}` — **not** the stream; `session_completed` `{ok: true}`; `score_viewed`; `share_clicked` `{channel: copy|linkedin}`. Never attach transcript, scores-as-quotes, emails, user ids, tokens. Recruiter vs candidate: same events; `utm`/`ref` on landing is enough to see “resume link” if the tool keeps campaign params (Plausible does; Vercel Hobby **UTM panel is not included** — Plus/Enterprise). **S3, S4, S6, S7**.

- **F8. Never send to analytics (audio/STT + note 18 + vendor redact lists).** Do not log: **audio blobs or bytes**; **playback/signed URLs** (note 18 F7: leaked link works until expiry); **transcript or STT text**; **voice embeddings / speaker-ID features** (note 18 F1/F11); **email, name, user id, guest token, auth query params**; **raw IP/UA** if you control the collector (vendors hash then discard — S2, S7); **session replay / heatmap of recorder or score UI** (F3, F5); **full answers or rubric quotes**. Safe: path, referrer, device class, CTA slot, permission **enum**, boolean “completed,” share **channel**. If a score number is sent, it can still be personal in a tiny-N portfolio — prefer “viewed” over the value. [not legal advice]

- **F9. GA4.** Official GA4 privacy/exemption pages **not read** this pass. CNIL F2: tools whose provider **reuses** measurement for their own purposes are outside the FR exemption. Treat GA4 as **consent + transfer analysis**, not the $0 privacy default. **[unconfirmed]**

- **F10. Speed Insights** is a separate Vercel product (perf), not the recruiter click funnel. Limits page not read. Ignore for event taxonomy.

## Conflicts and uncertainty

- **Consent-free analytics:** CNIL F2 (FR cookies Art. 82) ≠ ICO F3 (UK PECR statistical exception + object). Plausible “no banner” is vendor counsel **S7**, not CNIL/ICO certification. Do not blend; UK portfolio still needs inform + object if relying on F3.
- **Voice data vs analytics copy:** note 18 conflict (ICO vs FTC vs EDPB on “biometric”) is unchanged. Analytics must not become a second store of audio/transcript.
- PostHog / Umami Cloud **region, DPA, subprocessors** unread. Umami Cloud free quotas unread (pricing exit 2).
- Plausible Cloud **price** unread (https://plausible.io/pricing HTTP 404).
- Amplitude/Segment taxonomy unread — no claim they “standardize” interview-prep events.
- Vercel Hobby **personal-use / commercial** fair-use not read on the Hobby plan page; do not assume.
- GA4 / Schrems / CNIL GA orders not re-read here.
- Competitor live UI out of scope.

## Quotes

- “does not use cookies” / hash “valid for a single day” **S2**
- “Custom Events are available on Enterprise and Pro plans” **S4**
- “50,000 events / month included” (Hobby) **S3**
- “serve to produce anonymous statistical data only” (EN gist of FR “données statistiques anonymes”) **S5**
- “not for identifying, tracking or monitoring people” **S6**
- “logs or recordings of individual visitors to your website and the actions they took” **S6**
- “Raw IP addresses and User-Agent data are never stored.” **S7**
- “General text is not masked by default” **S10**
- “Usage stops at the free tier limits, so you can't be charged by surprise.” **S9**

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://vercel.com/docs/analytics/privacy-policy | Privacy and Compliance \| Vercel | updated 2026-06-26 | primary | Cookieless hash; fields; redact; [vendor] |
| S2 | https://vercel.com/docs/analytics | Vercel Web Analytics | unknown (fetched 2026-08-30) | primary | All plans; daily hash; [vendor] |
| S3 | https://vercel.com/docs/analytics/limits-and-pricing | Pricing for Web Analytics | updated 2026-08-25 | primary | Hobby 50k; no custom events; [vendor] |
| S4 | https://vercel.com/docs/analytics/custom-events | Tracking custom events | updated 2026-06-26 | primary | Pro/Enterprise only; 255-char cap; [vendor] |
| S5 | https://www.cnil.fr/fr/cookies-solutions-pour-les-outils-de-mesure-daudience | Cookies : solutions mesure d’audience \| CNIL | 2025-07-04 | primary | FR exemption; 13/25 mo; no cert |
| S6 | https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-exceptions/ | What are the exceptions? \| ICO | guidance finalized 2026-04-29 (index) | primary | PECR statistical exception; object |
| S7 | https://plausible.io/data-policy | Plausible data policy | last updated 2026-03 (page 2026-08-26) | primary | Daily hash; EU; [vendor] |
| S8 | https://plausible.io/self-hosted-web-analytics | Plausible CE / self-host | 2026-08-26 | primary | AGPL CE $0 to vendor; Cloud paid; [vendor] |
| S9 | https://posthog.com/pricing | PostHog pricing | unknown | primary | 1M events; stop at free; [vendor] |
| S10 | https://posthog.com/docs/session-replay/privacy | Session replay privacy controls | unknown | primary | Text unmasked by default; [vendor] |
| S11 | https://docs.umami.is/docs | Umami introduction (v3) | unknown | primary | Cookieless claim; Cloud/self-host; replay listed; [vendor] |

## Needs-browser

- https://umami.is/pricing — fetch.py exit 2 (thin/JS). Cloud free quotas unknown.
- https://plausible.io/pricing — fetch.py exit 4 (HTTP 404). Alternative not fetched (budget).
- https://amplitude.com/docs/data/create-and-maintain-a-taxonomy — not fetched (batch abort).
- https://segment.com/docs/connections/spec/track/ — not fetched (batch abort).
- https://www.cnil.fr/en/cookies-google-analytics-and-data-transfers-how-make-your-google-analytics-use-compliant-gdpr — not fetched (batch abort / guessed URL).

## Searched

- Vercel Web Analytics privacy
- CNIL cookies exemption analytics
- Plausible analytics GDPR cookies
- PostHog free tier limits
- ICO cookies analytics consent
- Umami analytics privacy docs
- Vercel Web Analytics Hobby limits
