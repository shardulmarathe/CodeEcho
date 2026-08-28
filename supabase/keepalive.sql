-- CodeEcho — keep the Render backend warm (pg_cron + pg_net)
-- ---------------------------------------------------------------------------
-- WHY: the backend is a Render free-tier web service. Render spins it down after
-- 15 minutes idle and a cold start costs ~1 minute. This schedules a lightweight
-- GET against a real app route often enough that it never sleeps.
--
-- WHY HERE and not GitHub Actions: this repo is public, and GitHub auto-disables
-- scheduled workflows after 60 days with no commits. Scheduled runs are also
-- explicitly best-effort and get delayed under load, which is unsafe against a
-- 15-minute deadline. Vercel Hobby cron is once-daily. pg_cron runs in a database
-- you already own, on time, with no third-party account.
--
-- ---------------------------------------------------------------------------
-- THE INSTANCE-HOUR BUDGET — read before changing the schedule
-- ---------------------------------------------------------------------------
-- Render free tier = 750 instance-hours per MONTH per workspace, and hours are
-- consumed while the service is AWAKE. So the ping spends the very resource it
-- protects:
--
--     24/7          ->  ~744 h/month  (31-day month)   6 h of margin. Too tight,
--                                                      and breaks entirely if you
--                                                      ever add a 2nd free service.
--     16 h/day      ->  ~496 h/month                   comfortable. <- default here
--
-- The window below is 08:00-23:59 Pacific. Nobody runs mock interviews at 4am, and
-- an off-hours visitor still gets the normal cold start plus the frontend's
-- warmBackend() head start (see frontend/src/lib/api.ts).
--
-- Supabase runs Postgres in UTC. 08:00 Pacific = 15:00 UTC (PDT, UTC-7), so the
-- window wraps midnight UTC: hours 15-23 and 0-6. Shift by one hour for PST.
--
-- ---------------------------------------------------------------------------
-- THE robots.txt TRAP — do not "optimise" the target URL
-- ---------------------------------------------------------------------------
-- While a free service is spun down, Render intercepts /robots.txt itself and
-- returns a disallow-all WITHOUT waking your container. Ping that and the monitor
-- goes green forever while the service sleeps. Always target a real app route.
-- /api/health is the right one: no LLM call, no DB write, no spend.
--
-- APPLIED 2026-08-28 to project izkyrcpmbfqtwkysvlje (codeecho). Verified: a one-off
-- net.http_get returned 200 {"status":"ok","gemini_configured":true,...}.
-- ---------------------------------------------------------------------------

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Idempotent: drop any previous version of the job before re-creating it.
select cron.unschedule('codeecho-backend-keepalive')
where exists (
  select 1 from cron.job where jobname = 'codeecho-backend-keepalive'
);

select cron.schedule(
  'codeecho-backend-keepalive',
  '*/14 15-23,0-6 * * *',   -- every 14 min (< Render's 15-min idle threshold)
  $$
    select net.http_get(
      url := 'https://fillerai-backend.onrender.com/api/health',
      -- MUST exceed a cold start. Measured 2026-08-28: cold /api/health = 31.4s,
      -- warm = 0.2s. At 30s the first ping timed out at 30001ms. It still WOKE the
      -- container (next request got an instant 200), but logged an error row on every
      -- cold landing, which would bury a real outage in net._http_response.
      timeout_milliseconds := 55000
    );
  $$
);

-- ---------------------------------------------------------------------------
-- Verify / operate
-- ---------------------------------------------------------------------------
--   select jobid, jobname, schedule, active from cron.job;
--
--   -- recent runs (did it fire, did it succeed).
--   -- NOTE: cron.job_run_details has no jobname column, only jobid -- must join.
--   select d.status, d.return_message, d.start_time
--   from cron.job_run_details d
--   join cron.job j on j.jobid = d.jobid
--   where j.jobname = 'codeecho-backend-keepalive'
--   order by d.start_time desc limit 20;
--
--   -- what the backend actually returned
--   select id, status_code, created
--   from net._http_response order by created desc limit 20;
--
--   -- turn it off
--   select cron.unschedule('codeecho-backend-keepalive');
