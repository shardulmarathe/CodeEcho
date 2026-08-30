# Category 13 — Latency / cold-start / perceived performance

**Evidence:** [`../notes/13-latency-coldstart.md`](../notes/13-latency-coldstart.md)  
**Repo:** `warmBackend()` already exists

## Bottom line

Render Free sleeps after **15 min**; wake ~**1 min**; **750** instance-hours/mo. Always-on keepalive ≈ **720–744h**—nearly exhausts the allotment (~6–30h slack). A loaded SPA does **not** get Render’s browser loading page—the UI must own an honest long wait (&gt;10s → progress + interrupt, not spinner-only or fake “ready”).

## Key evidence

- Keep-warm pings &lt;15 min keep the instance *running* (consumes hours); docs don’t ban inbound pings but outbound volume can suspend
- Vercel Hobby: no 15-min sleep; cron **once/day**—cannot keep Render warm
- Supabase pause ≈ 7 days inactivity; sub-15-min pg_cron→Render is overkill for Supabase and expensive for Render hours
- Skeletons OK under ~10s with honest wait copy; optimistic UI ≠ “API ready while origin sleeps”
- Health/liveness ≠ interview-ready

## Recommended CodeEcho actions

1. Named “Waking free-tier server (~1 min)…” with cancel / try sample path.
2. Do **not** aim for always-on on free Render; prefer on-demand warm + honest wait.
3. Revisit keepalive frequency vs 750h budget; don’t burn the month on pings.
4. Never show interview UI as ready before a real capability check.

## Sources

See note `13` (Render free, Vercel Hobby/cron, Supabase pause/cron, NN/g response times & skeletons, K8s probes).
