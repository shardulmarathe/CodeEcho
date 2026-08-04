# CodeEcho

SWE interview-prep platform. Answer software-engineering interview questions out loud; CodeEcho transcribes you and scores both your **reasoning** (STAR / technical rubrics) and your **delivery** (filler words, pace, pauses) — then tells you what to fix. Two modes: a guided **Mock Interview** session and a single-question **Practice** loop.

> Formerly "FillerAI" (filler-word speech analytics) — pivoted to interview prep.

**[Try it →](https://trycodeecho.vercel.app)**

## Stack

- **Frontend**: Next.js 16, React, Tailwind CSS (Vercel)
- **Backend**: FastAPI, containerized (Render, Docker web service)
- **Transcription**: Azure OpenAI Whisper, with Gemini fallback
- **Scoring**: Gemini via the Stanford AI Gateway or Google AI Studio
- **Database**: Supabase (Postgres + Storage + pgvector for retrieval)
- **Audio Processing**: FFmpeg

For how the scoring pipeline, retrieval layer and cost guards actually work, see
[ARCHITECTURE.md](./ARCHITECTURE.md).

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- FFmpeg (optional, for filler clip generation)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google `AIza...` key OR Stanford gateway `sk-...` key |
| `LLM_BASE_URL` | For Stanford keys | Default: `https://aiapi-prod.stanford.edu/v1` |
| `GEMINI_MODEL` | Yes | Text analysis model (e.g. `gemini-2.5-flash`) |
| `GEMINI_TRANSCRIPTION_MODEL` | No (default: `gemini-2.5-pro`) | Audio transcription model — use a multimodal model |
| `API_BUDGET_CAP_USD` | No (default: 5.0) | Hard spend cap |
| `SUPABASE_URL` | Later | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Later | Supabase service key |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL (default: http://localhost:8000) |

## Demo Mode

Without `GEMINI_API_KEY`, the backend runs in **demo mode** with mock transcript data.

### Stanford llm.stanford.edu (`sk-...` keys)

If your key is from [llm.stanford.edu](https://llm.stanford.edu) (same as `gemini-cli`):

```env
GEMINI_API_KEY=sk-your-stanford-key
GOOGLE_GEMINI_BASE_URL=https://api.llm.stanford.edu
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TRANSCRIPTION_MODEL=gemini-2.5-pro
```

Do **not** set `LLM_BASE_URL=https://aiapi-prod.stanford.edu` — that is a different UIT service.

### UIT AI API Gateway (separate service)

Only if you requested a key via Stanford UIT's AI API Gateway form:

```env
GEMINI_API_KEY=sk-your-uit-key
LLM_BASE_URL=https://aiapi-prod.stanford.edu/v1
GOOGLE_GEMINI_BASE_URL=
```

## API Budget

The backend tracks estimated API spend in `backend/data/budget_ledger.json`. Once the `$5` cap is reached, new analysis jobs are blocked.

## Supabase Setup

Run [`supabase/schema.sql`](supabase/schema.sql) in your Supabase SQL editor when ready to enable persistence.

## Project Structure

```
CodeEcho/
├── frontend/          # Next.js app
├── backend/           # FastAPI API
├── supabase/          # Database schema
└── docker-compose.yml
```

## Features (v1)

- [x] Audio upload and in-browser recording
- [x] Speech transcription (Gemini) with demo fallback
- [x] Filler detection with whitelist heuristics
- [x] FPM, WPM, pause analysis
- [x] Sentence position analysis
- [x] Idea transition analysis (Gemini)
- [x] Interactive timeline with clip playback
- [x] Tabbed results dashboard
- [x] API budget cap ($5)
- [ ] Cringe Reel (v2)
- [ ] Auth & session persistence (v2)
- [ ] Progress history dashboard (v2)
