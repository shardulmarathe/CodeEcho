# Category 18 — Privacy / audio retention

**Evidence:** [`../notes/18-privacy-audio.md`](../notes/18-privacy-audio.md)  
**Not legal advice.**

## Bottom line

Before Record, disclose **who / what (audio+transcript) / why / how long / who sees it / how to delete**. Private Supabase buckets + short-lived signed URLs are the discloseable free-stack pattern. A delete button does **not** replace a defined retention clock; delete must hit audio + transcript copies.

## Recommended CodeEcho actions

1. Just-in-time privacy blurb above Record + link to short policy.
2. Publish retention period or decision criteria; honor delete for audio+transcript.
3. Disclose private storage + signed URL expiry in policy.
4. Don’t over-claim “biometric” or “delete forever” unless true across backups.

## Conflicts

ICO (raw audio often not “biometric”) vs FTC (recordings as biometric information)—disclose practices clearly; get counsel for production.

## Sources

See note `18` (ICO, EDPB voice assistants, FTC biometric statement / Alexa blog, Supabase storage docs).
