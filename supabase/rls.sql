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
-- Do NOT add authenticated GRANTs or auth.uid() policies. FastAPI is the PEP.
-- The service-role key bypasses RLS; store._owns is the ownership check.
-- Child tables have no user_id, and pipeline persist has no user JWT, so
-- "RLS actually runs" for those writes would be theater. Guests are not
-- auth.uid() either. Keep this file default-deny.
-- ---------------------------------------------------------------------------
