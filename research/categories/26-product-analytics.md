# Category 26 — Product analytics (recruiter demo, $0)

**Evidence:** [`../notes/26-product-analytics.md`](../notes/26-product-analytics.md)  
**Aligns:** category 18 (privacy / audio)  
**Flags:** CNIL ≠ ICO; vendor “no banner” ≠ regulator certification

## Bottom line

On Vercel Hobby, use **Vercel Web Analytics page views only** (cookieless daily hash; **50k events/mo**; **custom events are Pro**). Encode the recruiter funnel as **routes** (`/`, `/practice`, `/score`, `/share`). Never send transcript, audio, signed URLs, or guest tokens (product rule; align cat 18). Session replay fails the **ICO** statistical exception for individual visit recordings; CNIL exemption conditions likely exclude it too (CNIL text does not name “replay” explicitly). PostHog replay defaults leave page text unmasked — leave replay off.

## Stack choice

| Option | Fit for $0 recruiter demo |
|--------|---------------------------|
| Vercel Web Analytics | Default: free on Hobby, cookieless, path funnel only |
| Plausible CE (self-host) | $0 to vendor if you pay infra; Cloud is paid |
| PostHog free | 1M events then ingestion stops; **leave replay off** |
| Umami | Cookieless claim; Cloud quotas unread this pass |
| GA4 | Treat as consent-required until proven otherwise |

## Event rules

**Hobby (no custom events):** path = event.  
**If Pro later:** `cta_clicked`, `mic_permission` (enum only), `score_viewed`, `share_clicked` — never content payloads.

**Never log:** audio blobs, transcripts/STT text, voice features, email/name, user id, guest token, signed URLs, replay of recorder/score UI.

## Regulator anchors

- **CNIL (FR, 2025-07-04):** audience-only exemption conditions (publisher-only, anonymous, inform, tracer ≤13 mo / data ≤25 mo) — not a certification.
- **ICO (UK):** statistical aggregate + inform + free object; individual recordings / profiling need consent.

## Recommended CodeEcho actions

1. Enable Vercel Web Analytics; `beforeSend` strip tokens/query PII; document `va-disable` opt-out.
2. Map IMPLEMENTATION milestones to distinct routes so path analytics answer “did they open sample vs practice?”
3. Skip session replay entirely on audio/score surfaces.

## Sources

See note `26` (S1–S11).
