# Category 25 — Threat model / ASVS checklist (guest + audio)

**Evidence:** [`../notes/25-threat-model-asvs.md`](../notes/25-threat-model-asvs.md)  
**Extends:** category 22 (guest/audio trust)  
**Scope:** defensive controls only — no exploit guidance

## Bottom line

For a free guest+audio demo, target **relevant ASVS 5.0 L1** plus **audio/PII L2** items — not an ASVS badge. One DFD + STRIDE-per-boundary is enough. Highest-leverage controls: upload allowlist + size caps with guest identified first, **authz on every API**, short-lived **private** signed URLs, CSP/CORS/Referrer locks, and anti-automation on STT/LLM spend.

## Implementable checklist (defensive)

| Area | Control | ASVS / source |
|------|---------|---------------|
| Upload | Size cap; extension + content allowlist; server-generated paths; no execution from public folders; identify guest before upload | V5 File Handling; File Upload Cheat Sheet |
| API | HTTPS; authz every endpoint; tokens not in URLs; 405/413/429; server state machine record→STT→score | V4 API; REST Security CS |
| Frontend | Disable unused CORS; else allowlisted Origin; CSRF via token or non-simple header; CSP L2; HSTS; nosniff; Referrer-Policy; frame-ancestors | V3 Frontend |
| Data | Classify audio/transcript/score; document retention; `Cache-Control: no-store`; no secrets in Web Storage; rate-limit STT/LLM | V14; V2 anti-automation |
| Tokens | Opaque guest ID (V7) or JWT (V9); CSPRNG ≥128 bits; UUID object names only if guest token authorizes access | V11 crypto |
| Signed URLs | Private bucket; server `createSignedUrl`; prefer TTL ≪ vendor 3600s example; Referrer-Policy | Supabase downloads docs |

## Threat-model shape

Assets: guest browser, Next.js, FastAPI, Supabase, STT, tokens/audio/transcripts/scores.  
Method: DFD + STRIDE per trust boundary; Shostack Mitigate / Eliminate / Transfer / Accept.

## Recommended CodeEcho actions

1. Document retention + delete path (L2); automatic delete is L3 — honesty in UI if not automated.
2. Shorten signed URL TTL vs default hour; keep guest token out of query strings.
3. README trust note: what is stored, how long, how to delete (align cat 18/22).

## Sources

See note `25` (S1–S14).
