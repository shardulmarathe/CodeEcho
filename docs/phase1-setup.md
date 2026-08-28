# Phase 1 Setup: Auth, Persistence, Guest Mode, Rate Limiting

Phase 1 is **Supabase Auth** (magic link, optional Google), **Supabase** persistence
(backend-mediated), a **guest mode** (localStorage UUID, claimed on signup), and
**rate limiting**.

The app **runs today without any of this configured**, it falls back to guest-only
mode with in-memory storage. Configure the services below to enable accounts and
durable history.

---

## 1. Supabase (Postgres + Storage + pgvector)

1. Create a project at <https://supabase.com/dashboard>.
2. **SQL editor → New query →** paste all of [`supabase/schema.sql`](../supabase/schema.sql) and run it.
   (It enables the `vector` extension and creates `attempts`, `delivery_metrics`,
   `questions`, `scorecards`, `guests`, `profiles`, `kb_documents`, …)
3. **Storage → New bucket →** name it `audio`, keep it **Private** (audio and filler
   clips are served via short-lived signed URLs).
4. **Project Settings → API →** copy:
   - `Project URL` → `SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_URL`
   - `anon` / publishable key → `NEXT_PUBLIC_SUPABASE_ANON_KEY` (frontend only)
   - `service_role` secret key → `SUPABASE_SERVICE_ROLE_KEY`  ← **backend only**
   Skip JWT Keys / Legacy JWT Secret. FastAPI verifies new ECC tokens via JWKS at `SUPABASE_URL`.
5. **Authentication → Providers →** enable Email (magic link). Google only if you
   already have OAuth credentials.
6. **Authentication → URL configuration →** add `http://localhost:3000/auth/callback`
   plus production/preview callback URLs.

Backend `backend/.env`:
```env
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...service-role...
SUPABASE_STORAGE_BUCKET=audio
```

Frontend `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...anon...
```

The backend verifies access tokens from JWKS at `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`
(`aud=authenticated`). The frontend never sees the service-role key.

## 2. Run

```bash
# backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm install && npm run dev
```

---

## Security model (how secrets are protected)

- **Frontend** only ever sees `NEXT_PUBLIC_*` values (API URL + Supabase anon key).
  The Gemini key, Supabase **service-role** key, and **JWT secret** live **only** in
  `backend/.env` and never reach the browser bundle.
- **Backend-mediated**: the frontend talks only to FastAPI; FastAPI is the sole
  Supabase client (service-role key). Every query is scoped to the verified
  `user_id` (or guest token). Do not add `authenticated` GRANTs or user-JWT
  PostgREST — RLS stays default-deny.
- **Rate limiting**: per-identity on expensive routes (signed-in users by user id,
  everyone else by IP) + the existing `$` budget cap.
- `.env` / `.env.local` are gitignored.

## Verifying it works

- `GET /api/health` reports `auth_configured` / `supabase_configured`.
- Sign in → `POST /api/attempts/claim` transfers prior guest attempts (and
  interview sessions) to your account. The guest token is the `X-Guest-Token`
  header, never a body field.
- Exceeding `RATE_LIMIT_EXPENSIVE` returns **429**.
- A second user/guest reading another's attempt returns **404**.
