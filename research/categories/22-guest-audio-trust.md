# Category 22 — Guest token & signed audio trust (defensive)

**Evidence:** [`../notes/22-guest-audio-trust.md`](../notes/22-guest-audio-trust.md)  
**Scope:** defensive hygiene only — no exploit detail

## Bottom line

Guest tokens and signed audio URLs are **bearer secrets**. Mint unguessable tokens, verify server-side, short expiry; keep audio in a **private** bucket with server-minted signed URLs; rate-limit mint/upload; disclose in README what is stored and that this is **not** a formal security assessment.

## Recommended CodeEcho actions

1. Confirm guest token entropy + server validation + idle/absolute expiry.
2. Keep signed URL TTLs short; never put service role key in the client.
3. Rate-limit guest creation, uploads, and URL minting.
4. README privacy/security blurb: retention, private bucket, bearer-URL warning.

## Sources

See note `22` (OWASP session/ASVS/API4, NIST 800-63B session, Supabase storage fundamentals/downloads, OWASP privacy/logging cheat sheets).
