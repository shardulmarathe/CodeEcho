-- CodeEcho — Row Level Security (Phase 1: default-deny hardening)
-- ---------------------------------------------------------------------------
-- WHY: Supabase exposes every public table over its auto REST/GraphQL API. The
-- project's ANON key is public by design (it ships to browsers). With RLS OFF,
-- anyone with the project URL + anon key can read/write these tables directly,
-- bypassing all backend ownership checks.
--
-- WHAT THIS DOES: enables RLS on every table and adds NO permissive policies for
-- the anon/authenticated roles => those roles get ZERO access (default deny).
-- The FastAPI backend uses the SERVICE-ROLE key, which BYPASSES RLS, so it keeps
-- full access and needs no code changes. This is safe to run as-is.
--
-- Run this in the Supabase SQL editor AFTER schema.sql. Idempotent.
-- ---------------------------------------------------------------------------

alter table profiles            enable row level security;
alter table guests              enable row level security;
alter table questions           enable row level security;
alter table attempts            enable row level security;
alter table delivery_metrics    enable row level security;
alter table transcript_words    enable row level security;
alter table fillers             enable row level security;
alter table scorecards          enable row level security;
alter table interview_sessions  enable row level security;
alter table kb_documents        enable row level security;
alter table api_budget          enable row level security;
alter table api_usage_daily     enable row level security;

-- Belt-and-suspenders: also revoke the API-facing role grants so the tables are
-- not exposed even if a future policy is added by mistake. (service_role and the
-- table owner are unaffected and retain full access.)
revoke all on all tables in schema public from anon, authenticated;

-- Keep the spend-increment RPC callable only by the backend (service_role), never
-- via the public anon key. Run this AFTER schema.sql has created the function.
revoke all on function increment_api_usage(date, text, double precision)
  from anon, authenticated;

-- ---------------------------------------------------------------------------
-- PHASE 2 (optional, later): real per-user RLS enforced by Postgres.
-- Only needed if you move any reads to the CLIENT (frontend talks to Supabase
-- directly instead of through the FastAPI backend). Steps:
--   1. Configure Clerk as a Supabase third-party auth provider (Supabase docs:
--      "Clerk" integration) so Postgres can read Clerk's `sub` from the JWT.
--   2. Grant the authenticated role scoped access and add owner policies, e.g.:
--
--      grant select, insert, update, delete on attempts to authenticated;
--      create policy "own attempts (user)" on attempts
--        for all to authenticated
--        using (user_id = auth.jwt()->>'sub')
--        with check (user_id = auth.jwt()->>'sub');
--
--   Guests have no Supabase identity (their token is client-minted), so guest
--   rows would stay backend-only — keep guest reads/writes going through the API.
-- ---------------------------------------------------------------------------
