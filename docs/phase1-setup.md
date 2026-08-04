# Phase 1 Setup: Auth, Persistence, Guest Mode, Rate Limiting

Phase 1 reshapes CodeEcho into the SWE interview-prep foundation: **Clerk** auth,
**Supabase** persistence (backend-mediated), a **guest mode** (5 free attempts that
transfer to your account on signup), and **rate limiting**.

The app **runs today without any of this configured**, it falls back to guest-only
mode with in-memory storage. Configure the services below to enable accounts and
durable history.

---

## 1. Supabase (Postgres + Storage + pgvector)

1. Create a project at <https://supabase.com/dashboard>.
2. **SQL editor → New query →** paste all of [`supabase/schema.sql`](../supabase/schema.sql) and run it.
   (It enables the `vector` extension and creates `attempts`, `delivery_metrics`,
   `questions`, `scorecards`, `guests`, `profiles`, `kb_documents`, …)
3. **Storage → New bucket →** name it `audio`, keep it **Private** (audio is served via
   short-lived signed URLs).
4. **Project Settings → API →** copy:
   - `Project URL` → `SUPABASE_URL`
   - `service_role` secret key → `SUPABASE_SERVICE_ROLE_KEY`  ← **backend only, never the frontend**

Put these in `backend/.env`:
```env
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...service-role...
SUPABASE_STORAGE_BUCKET=audio
```

## 2. Clerk (auth)

1. Create an application at <https://dashboard.clerk.com>.
2. **API Keys →** copy the **Publishable key** and **Secret key**.
3. **Frontend API URL** (shown under API Keys / "Show API URLs"), e.g.
   `https://your-app.clerk.accounts.dev` → this is the **issuer**.

Frontend `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

Backend `backend/.env`:
```env
CLERK_ISSUER=https://your-app.clerk.accounts.dev
# CLERK_JWKS_URL=            # optional; auto-derived from CLERK_ISSUER
GUEST_ATTEMPT_LIMIT=5
```

The backend verifies Clerk session JWTs against Clerk's JWKS (RS256). No Clerk secret
is required on the backend just to verify tokens, `CLERK_ISSUER` is enough.

## 3. Run

```bash
# backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm install && npm run dev
```

---

## Security model (how secrets are protected)

- **Frontend** only ever sees `NEXT_PUBLIC_*` values (API URL + Clerk *publishable* key).
  The Gemini key, Supabase **service-role** key, and Clerk **secret** key live **only** in
  `backend/.env` and never reach the browser bundle.
- **Backend-mediated**: the frontend talks only to FastAPI; FastAPI is the sole Supabase
  client (service-role key). Every query is scoped to the verified Clerk `user_id` (or guest
  token), so users can only access their own attempts.
- **Rate limiting**: per-IP limits (`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_EXPENSIVE`) + the
  guest 5-attempt cap + the existing `$` budget cap.
- `.env` / `.env.local` are gitignored.

## Verifying it works

- `GET /api/health` reports `clerk_configured` / `supabase_configured`.
- Guest: `GET /api/me` shows `guest_remaining`; the 6th attempt returns **402**.
- Sign in → a `POST /api/attempts/claim` transfers prior guest attempts to your account.
- Exceeding `RATE_LIMIT_EXPENSIVE` returns **429**.
- A second user/guest reading another's attempt returns **404**.
