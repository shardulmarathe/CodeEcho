# 22 — Guest tokens and signed audio URLs (defensive trust boundaries)

**Worker:** research-worker · **Budget used:** 24/12 calls (cap 20) · **Date:** 2026-08-30

**Worker scope:** High-level defensive hygiene for guest tokens (`X-Guest-Token`) and signed audio URLs on a free interview demo. Official OWASP / NIST / Supabase only. No exploit PoCs, attack procedures, or bypass recipes. Offensive WSTG / API4 attack-scenario bodies skipped.

## Findings

- **Design threats: token disclosure / capture / prediction / reuse.** [S1]: a live session ID is “temporarily equivalent to the strongest authentication method”; disclosure, capture, prediction, brute force, or fixation enable impersonation. Treat `X-Guest-Token` as that class of secret. [S2]: sessions unique, unguessable, unshared; invalidate when unused; idle-timeout.

- **URL-borne secrets leak (logs, history, Referer, search).** [S1]: IDs in URLs appear in “web links and logs, web browser history and bookmarks, the Referer header or search engines.” Signed audio URLs are the same capability class until expiry. Keep *session* identity off the URL; keep object URLs short-lived and single-purpose.

- **Enumeration / IDOR is authorization, not “private bucket.”** [S5] L1: function-level *and* data-specific access (named IDOR/BOLA); enforce on a trusted service layer, not client JS (8.3.1). [S7]: SELECT without `storage.allow_any_operation()` can list objects. Authorize each audio object at FastAPI mint time.

- **Mint/verify like a session secret; never a static API key.** [S2] 7.2.1–7.2.3: backend verify; dynamic tokens; CSPRNG; **≥128 bits** entropy. [S1] floor **≥64 bits** (homemade IDs: ≥128). [S12] session secrets: approved RNG, **≥64 bits**, issued at auth, timed out, not available to intermediaries. Reject IDs the server never issued ([S1] strict mode).

- **Expiry must be server-enforced.** [S1]: idle + absolute; idle “2-5 minutes” (high-value) / “15-30 minutes” (low-risk); absolute often 4–8 h; kill **server-side**. [S9][S12]: overall vs inactivity; either **SHALL** terminate; activity resets idle only. AAL1 overall **SHOULD ≤30 days**, idle **MAY**; AAL2 **SHOULD ≤24 h / ≤1 h idle**; AAL3 **SHALL ≤12 h / SHOULD ≤15 min idle**. Guest ≈ AAL1 assurance, but [S1] still wants short windows. [S2] 7.4: reference tokens die in the backend; self-contained tokens need a block-list / issued-before cutoff / key rotation.

- **HttpOnly/Secure/SameSite for cookies; not for JS storage or custom headers.** [S1][S9]: `Secure`, `HttpOnly`, `SameSite=Strict|Lax`, `__Host-` + `Path=/`; opaque; no PII in the cookie; cookie `Max-Age` **SHALL NOT** be the only timeout; **do not** store tokens in `localStorage`/`sessionStorage`. `X-Guest-Token` is a listed exchange mechanism [S1] but is JS-readable (no HttpOnly). Prefer an HttpOnly cookie from FastAPI, or treat the header as XSS-equivalent to Web Storage.

- **Private bucket + server-minted signed URL; Auth rotation does not revoke.** [S8]: private **by default**; download via JWT+RLS or time-limited `createSignedUrl`. Public: anyone with the URL. [S3]: sign on the server; dedicated storage key **≠** Auth JWT; valid until expiry despite Auth rotation; revoke = contact support; docs example **3600 s**. [S7]: RLS default-deny; scope by bucket/folder/`sub`/`owner_id`; **service key bypasses RLS** — do not ship it. Mint a short URL only after the guest owns the object.

- **Rate / size / spend limits.** [S10] prevention only: rate-limit API calls; tighter caps on expensive ops; max upload/payload; timeouts; billing alerts for paid STT/LLM. [S1]: `Cache-Control: no-store` (and `Clear-Site-Data` on logout) for responses that carry session IDs or signed URLs.

- **README: honesty, not an audit badge.** No official “portfolio README” template. Required *documentation*: idle+absolute and NIST deviations [S2] 7.1.1; function/data rules [S5] 8.1.1; documented time limits [S9]. [S11]: if you cannot prevent log/data misuse, “the truth must be told.” [S4]: anonymous/pseudonymous when real identity is not required. [S6]: log authz/session failures, uploads, consent; **do not log** session IDs, access tokens, secrets, sensitive PII; honor stated retention. [S12]: releasing personal information online ⇒ **≥AAL2** for federal systems — a voice demo should say it is **not** that bar. Implied README: what is stored; retention; private bucket + short URLs; bearer secrets (don’t share); no service keys in repo; rate limits; not an ASVS/NIST assessment.

## Conflicts and uncertainty

- **Entropy floor:** [S1] 64-bit session entropy vs [S2] 128-bit reference-token entropy vs [S12] 64-bit session-binding secret. Same [S1] page also says homemade IDs should be ≥128-bit CSPRNG. For a guest token, follow the **stricter ASVS L1 128-bit** bar; do not treat 64-bit as “ASVS-aligned.”
- **Idle timeout:** [S12] AAL1 idle is optional / 30-day overall; [S1] still wants idle+absolute in minutes–hours. A recruiter demo should follow **OWASP short windows**, not AAL1’s 30-day SHOULD, because guest tokens are bearer and often JS-visible.
- **Revocation:** [S3] signed URLs live until expiry unless Supabase support revokes; [S2] 7.4.1 expects app-controlled terminate for self-contained tokens. Product gap: **expiry is the revoke you control**; deleting/renaming the object is the other first-party lever (not independently documented as “revoke” on the pages read).
- **HttpOnly vs `X-Guest-Token`:** official cookie advice does not bless custom headers. Header tokens inherit XSS/disclosure risk of JS-accessible secrets [S1][S9].
- **ASVS V5 File Handling and Authorization Cheat Sheet** not fetched (budget). File-type/size bucket limits [S8] are the only first-party file-restriction text used.
- API4 [S10] “Example Attack Scenarios” skipped (offensive). Prevention list only.
- Official sources do not specify a README template; disclosure bullets are a mapping, not a quote.

## Quotes

> "The disclosure, capture, prediction, brute force, or fixation of the session ID will lead to session hijacking" [S1]
> "Sessions are unique to each individual and cannot be guessed or shared." [S2]
> "Signed URLs remain valid until their expiry time regardless of any Auth key changes." [S3]
> "organizations can use anonymous or pseudonymous accounts." [S4]
> "data-specific access is restricted to consumers with explicit permissions to specific data items" [S5]
> "The following should usually not be recorded directly in the logs" [S6]
> "Service keys entirely bypass RLS policies" [S7]
> "Buckets are private by default." [S8]
> "SHOULD NOT be placed in insecure locations (e.g., HTML5 Local Storage)" [S9]
> "Implement a limit on how often a client can interact with the API" [S10]
> "the truth must be told to the users in a clear understandable form" [S11]
> "An inactivity timeout MAY be applied but is not required at AAL1." [S12]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html | Session Management Cheat Sheet | unknown (fetched 2026-08-30) | primary | OWASP; cookies, URL leak, timeouts |
| S2 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x16-V7-Session-Management.md | ASVS 5.0 V7 Session Management | 2025-05 (v5.0.0) | primary | Entropy 128; backend verify; revoke |
| S3 | https://supabase.com/docs/guides/storage/serving/downloads | Serving assets from Storage | 2026-08-28 | primary | Private vs public; sign key; no Auth revoke |
| S4 | https://pages.nist.gov/800-63-4/sp800-63.html | NIST SP 800-63-4 | 2025-08-26 | primary | Anon/pseudonym; privacy with security |
| S5 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x17-V8-Authorization.md | ASVS 5.0 V8 Authorization | 2025-05 (v5.0.0) | primary | IDOR/BOLA; trusted service layer |
| S6 | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html | Logging Cheat Sheet | unknown (fetched 2026-08-30) | primary | Exclude tokens; retention; consent |
| S7 | https://supabase.com/docs/guides/storage/security/access-control | Storage Access Control | 2026-08-28 | primary | RLS default deny; no public service key |
| S8 | https://supabase.com/docs/guides/storage/buckets/fundamentals | Storage Buckets | 2026-08-28 | primary | Private default; two download paths |
| S9 | https://pages.nist.gov/800-63-4/sp800-63b/session/ | NIST SP 800-63B-4 Session Management | 2025-08-26 | primary | Cookie flags; bearer vs PoP; document limits |
| S10 | https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/ | API4:2023 Unrestricted Resource Consumption | 2023 | primary | Prevention: rate/size/spend limits only |
| S11 | https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html | User Privacy Protection Cheat Sheet | unknown (fetched 2026-08-30) | primary | Honesty if logs/data cannot be protected |
| S12 | https://pages.nist.gov/800-63-4/sp800-63b.html | NIST SP 800-63B-4 | 2025-08-26 | primary | AAL timeout numbers; ≥AAL2 if PII online |

## Needs-browser

*(none — all official HTML/raw fetched exit 0)*

## Searched

OWASP session management cheat sheet, OWASP ASVS access control, Supabase storage signed URLs, NIST SP 800-63 authentication, OWASP logging cheat sheet, Supabase storage access control, NIST 800-63B session timeout, OWASP REST security rate limit
