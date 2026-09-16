# CodeEcho

SWE interview-prep platform. You answer interview questions out loud; CodeEcho transcribes you and
scores two independent things — **reasoning** (STAR / technical rubrics) and **delivery** (filler
words, pace, pauses) — then says what to fix. Two modes: guided Mock Interview, single-question Practice.

## Verify
```bash
cd frontend && npx tsc --noEmit       # no typecheck script; this is the check
cd backend  && python -m pytest        # requires backend deps installed
docker compose up                      # backend :8000, frontend :3000
```

## Layout
- `backend/` — FastAPI. Own `requirements.txt`, own `tests/`. `backend/clips/`, `uploads/`,
  `data/` are runtime artifacts, not source.
- `frontend/` — Next.js. Own `package.json` **and its own `vercel.json`** — it deploys independently.
- `supabase/` — schema.

## Invariants
- **Reasoning and delivery are scored separately and must stay separable.** A fluent answer that
  is wrong and a correct answer delivered badly are different failures, and the product's value is
  telling them apart. Don't collapse them into one score.
- Delivery metrics are measured from the transcript + audio, never inferred from the reasoning
  score (or vice versa).

## Currently migrating away from
- **Formerly "FillerAI"** — a filler-word speech-analytics tool, pivoted to interview prep. Expect
  stale `fillerai` identifiers, env var names, and deploy references. New code uses CodeEcho naming;
  don't reintroduce the old one, and don't assume a `filler*` symbol is dead until you've checked.

## Deploys on Render — the constraints that actually bite

`render.yaml` at the root is a Blueprint: **backend on Render (Docker, free tier, oregon),
frontend independently on Vercel** via `frontend/vercel.json`. Two deploy targets, one repo.

- **512 MB total on the free tier, and the local cross-encoder reranker is ~150–200 MB of ONNX.**
  It OOM-killed the worker during scoring, so production runs `RERANK_ENABLED=false` — a
  **deliberate precision downgrade, not a bug.** Local dev runs it `true`. Do not "fix" the flag.
- **The filesystem is ephemeral.** Local writes are lost on every deploy, restart, and spin-down.
  Anything that must persist goes to the database or object storage.
- **Bind to `0.0.0.0:$PORT`**, never `127.0.0.1` and never a hardcoded port.
- **Free web services spin down after 15 minutes idle**, so the first request after a quiet period
  pays a cold start. Free Postgres expires after 30 days.
- **Render runs Linux: paths are case-sensitive.** An import that works on this Mac can fail there.
- Secrets are `sync: false` in `render.yaml` and set in the dashboard. **Never commit a value.**

These are written here rather than left to a Cursor plugin rule, because that rule is invisible to
Claude Code and disappears if the plugin is uninstalled. A constraint that only one tool can see
is a constraint that gets violated by the other.

## Gotchas
- The frontend has **no typecheck script**, so nothing catches type errors in CI. Run
  `npx tsc --noEmit` in `frontend/` explicitly before claiming a change is safe.
- `.gitignore` used to exclude all of `.claude/` and `.cursor/`; it is now narrowed to
  `settings.local.json` so shared config is actually committed.

<!-- Owner: me. Reviewed 2026-09-14. frontend tsc --noEmit run: rc=0. -->
