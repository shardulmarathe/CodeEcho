# 25 — ASVS-aligned defensive checklist (guest + audio demo)

**Worker:** research-worker · **Date:** 2026-08-30 · **Scope:** Defensive-only ASVS 5.0 / Cheat-Sheet mapping for a free guest+audio interview demo. No exploit PoCs. Deepens note 22; does not replace session/signed-URL hygiene.

## Findings

- **F1. V5 File Handling — L1 floor for audio.** [S2] Files → DoS, unauthorized access, storage exhaustion. **5.1.1 (L2):** document types, extensions, max size (incl. unpacked), malicious-file behavior. **5.2.1 (L1):** size the app can process without DoS. **5.2.2 (L1):** extension *and* contents match (magic bytes / libraries); L1 may limit to files used for business/security decisions. **5.2.3 (L2):** compressed max uncompressed size + file count *before* unpack. **5.2.4 (L3):** per-user quota + max file count. **5.3.1 (L1):** untrusted files in a public folder must not execute as code. **5.3.2 (L1):** internally generated paths. **5.4.1–5.4.2 (L2):** ignore/validate user filenames; `Content-Disposition`; RFC 6266 encoding. **5.4.3 (L2):** AV before serving. Demo: audio allowlist; server object key; private bucket; size cap before STT.

- **F2. File Upload CS.** [S1] Allowlist extensions (validate input first); do not trust `Content-Type`; server-generated name; length/charset limits; size limit; authorize first; different host or outside webroot; public access via opaque id→file; AV if available; CSRF-protect; patch parsers. Uploader must be registered **or identifiable** so limits apply; authz to access/modify. Least-privilege FS. Measure zip size after safe decompress. Download request limits. ZIP “not recommended.” UUID/GUID is the sheet’s rename — see F9 conflict.

- **F3. Threat model at demo scale.** [S3] Four questions (Manifesto): what are we working on / can go wrong / will we do / did we do enough. DFD (whiteboard OK): **trust boundaries, data flows, data stores, processes, external entities**. Tools: Threat Dragon, Microsoft TMT, pytm, draw.io. Cloud: shared responsibility, managed APIs, **storage buckets**, IAM, serverless. STRIDE → authn / integrity / accounting / confidentiality / availability / authorization. Shostack: **Mitigate, Eliminate, Transfer, Accept**. Review: DFD accurate; each threat has a response; mitigations testable. Microsoft [S10] (2022-08-25): Spoofing = using another’s auth info; Tampering = change stored or in-transit data; Repudiation = deny an action with no proof; Disclosure = read without access; DoS = deny service; EoP = unprivileged → privileged. One DFD + STRIDE-per-boundary; not PASTA/OCTAVE.

- **F4. DFD assets for this stack** (official element types applied). [S3][S10] Entities: guest browser, STT vendor. Processes: Next.js, FastAPI, Supabase. Stores: guest tokens, private audio, transcripts, scores. Boundaries: browser↔Next, Next↔FastAPI, FastAPI↔Supabase, FastAPI↔STT. STRIDE *prompts* only: spoof guest token; tamper score; missing upload logs; URL/Referer leak; large/rapid upload or STT spend; mint URL for another guest’s object.

- **F5. REST + V3/V4 browser/API.** [S4][S5][S6] HTTPS; authz **at each** endpoint; no session-in-body. Methods allowlist → **405**; size → **413**; rate/DoS → **429**. Tokens **not in URLs**. CORS: disable if no cross-origin JS; else specific origins. **3.4.2 (L1):** ACAO fixed or Origin allowlisted; `*` only if response has **no** sensitive data. **3.5.1–3.5.3 (L1):** CSRF token or non-safelisted header; mutating methods not GET; if relying on preflight, action must not be a “simple” request. **3.2.1 (L1):** wrong-context render of APIs/uploads (`Sec-Fetch-*`, CSP sandbox, or `Content-Disposition: attachment`). **3.4.1 (L1):** HSTS ≥1 year. **3.4.3 (L2):** CSP with `object-src 'none'`, `base-uri 'none'`, allowlist or nonces/hashes. **3.4.4–3.4.6 (L2):** nosniff; Referrer-Policy (signed-URL path/query); `frame-ancestors` (XFO obsolete). API browser headers [S4]: `Cache-Control: no-store`; `CSP: frame-ancestors 'none'`; HSTS; nosniff. **4.1.1 (L1):** matching `Content-Type`+charset. **4.1.3 (L2):** client cannot override `X-Forwarded-*` / `X-User-ID`. Workflow [S4]+**2.3.1:** server state machine record→upload→STT→score.

- **F6. V14 + V2 — PII/audio, delete, anti-automation.** [S7][S8] **14.2.1 (L1):** secrets only in body/headers. **14.1.1–14.1.2 / 14.2.4 (L2):** classify audio/transcript/scores; document encryption, integrity, **retention**, logging. **14.2.7 (L3):** retention class + **automatic delete**. **14.3.1 (L1):** clear client storage on logout (`Clear-Site-Data`). **14.3.2–14.3.3 (L2):** `no-store`; no sensitive data in Web Storage except session tokens. **2.2.1–2.2.2 (L1):** allowlist at a trusted service layer. **2.1.3 / 2.3.2 (L2):** per-user *and* global limits. **2.4.1 (L2):** anti-automation vs quota exhaustion, DoS, **costly resources** (STT/LLM).

- **F7. V9/V11 tokens vs UUID.** [S9][S11] Opaque guest ID → V7 (note 22). Self-contained JWT → V9 L1: verify MAC/sig; algorithm allowlist, no `None`; pre-configured keys. **11.5.1 (L2):** CSPRNG **≥128 bits**; “UUIDs do not respect this condition.” UUID is OK as a *storage name* only if access is gated by the guest token + server mint, not by knowing the path.

- **F8. Levels + vendor TTL + CISA.** [S12] L1 ≈ 20%, first-layer, “critical starting point.” L2 is what most apps should strive for (all L1+L2 ≈ 70% of catalog). Documentation reqs are separately verifiable. **Not an ASVS badge.** Target: relevant L1 + L2 that protect audio (CSP, quotas, classify, `no-store`, 2.4.1, Referrer-Policy). [S13] Private bucket; server `createSignedUrl`; storage key ≠ Auth JWT; valid until expiry; revoke = support; example **3600 s**. [S14] Landing only: security as a core requirement; MFA/logging/SSO “at no extra cost.” Whitepaper unread. Transfer: default-deny + security logs, not paid-gated basics.

### Checklist

| Surface | Cite | Action |
|---------|------|--------|
| Guest token | note 22; 11.5.1; 14.2.1; [S4] | CSPRNG ≥128-bit opaque; not in URL; HttpOnly cookie preferred; server TTL |
| Signed URL | [S13]; 3.4.5; 14.2.1 | Private bucket; mint after ownership; short TTL; Referrer-Policy; `no-store` |
| Audio upload | V5.2.1–5.3.2; [S1] | Audio magic+ext; size cap; server key; CSRF/non-simple; identifiable guest |
| STT/score | 2.3.1; 2.4.1; [S4] | Server state machine; 413/429; STT/LLM spend cap |
| Scores/transcripts | V8 note 22; 14.1–14.2 | Per-guest authz; classify; retention + delete path |
| Browser/API | 3.4.1–3.4.4; [S4] | HSTS; CORS allowlist (no `*`+tokens); CSP L2; nosniff; frame-ancestors none |
| Logs | [S4]; note 22 | Failures yes; tokens/signed URLs/audio no |

## Conflicts and uncertainty

- **UUID vs 128-bit:** [S1] UUID names vs [S11] UUIDs fail 11.5.1. Path ≠ authorization secret.
- **L1 vs L2:** [S12] L1 is the official start; audio/PII makes several L2 items first-class. Not an assessment.
- **Revoke:** [S13] expiry or support only (same as note 22).
- CISA whitepaper unread. Forgot Password CS N/A. [S10] auth interstitial but STRIDE table returned. asvs.dev TOC exit 4; chapters/raw OK. Offensive blogs not used.

## Quotes

> "UUIDs do not respect this condition." [S11]
> "Disable CORS headers if cross-domain calls are not supported/expected." [S4]
> "Signed URLs remain valid until their expiry time regardless of any Auth key changes." [S13]
> "overuse of costly resources" [S8]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html | File Upload Cheat Sheet | unknown (fetched 2026-08-30) | primary | OWASP `--full` |
| S2 | https://asvs.dev/v5.0.0/V5-File-Handling/ | ASVS 5.0 V5 File Handling | 2025-05 | primary | Full chapter |
| S3 | https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html | Threat Modeling Cheat Sheet | unknown | primary | DFD + STRIDE + Shostack |
| S4 | https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html | REST Security Cheat Sheet | unknown | primary | CORS, 413/429 |
| S5 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md | ASVS 5.0 V3 Frontend | 2025-05 | primary | CORS L1; CSP L2 |
| S6 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x13-V4-API-and-Web-Service.md | ASVS 5.0 V4 API | 2025-05 | primary | Content-Type L1 |
| S7 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x23-V14-Data-Protection.md | ASVS 5.0 V14 Data Protection | 2025-05 | primary | Retention L3 |
| S8 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x11-V2-Validation-and-Business-Logic.md | ASVS 5.0 V2 Validation | 2025-05 | primary | Anti-automation |
| S9 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x18-V9-Self-contained-Tokens.md | ASVS 5.0 V9 Tokens | 2025-05 | primary | JWT only if used |
| S10 | https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats | Microsoft TMT STRIDE | 2022-08-25 | primary | Category defs |
| S11 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x20-V11-Cryptography.md | ASVS 5.0 V11 Cryptography | 2025-05 | primary | CSPRNG ≥128 |
| S12 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md | What is the ASVS | 2025-05 | primary | L1 ~20% |
| S13 | https://supabase.com/docs/guides/storage/serving/downloads | Serving assets from Storage | 2026-08-28 | primary | [vendor] 3600s |
| S14 | https://www.cisa.gov/securebydesign | CISA Secure by Design | unknown | primary | Landing only |

## Needs-browser

- https://asvs.dev/v5.0.0/ — fetch.py exit 4; chapter/raw fetches succeeded.
- CISA joint-guidance PDF linked from [S14] — not fetched.

## Searched

OWASP ASVS 5.0, OWASP File Upload Cheat, OWASP Threat Modeling STRIDE, OWASP REST Security CORS
