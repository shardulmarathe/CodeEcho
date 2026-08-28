from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.routes import router
from app.services.ratelimit import limiter

app = FastAPI(
    title="CodeEcho API",
    description="SWE interview-prep platform — delivery analysis + scorecards",
    version="0.2.0",
)

# Rate limiting (per client IP), protects against abuse and runaway LLM spend
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
def _warm_models() -> None:
    """Pre-load the RAG reranker locally so the first scored answer isn't slowed by a
    cold model load. Skipped on Render — free tier has 512MB RAM and loading the
    cross-encoder (~200MB ONNX) there causes OOM during scoring."""
    import os
    import threading

    if os.getenv("RENDER") == "true":
        return

    from app.services import reranker

    if reranker.is_enabled():
        threading.Thread(target=reranker.warm, name="rerank-warm", daemon=True).start()

if settings.enable_debug_routes:
    from app.routes_debug import router as debug_router

    app.include_router(debug_router, prefix="/api")

# Ensure local media dirs exist. Audio is served via the guarded GET /api/audio
# route (or Supabase signed URLs in prod). The public StaticFiles mount at /clips
# is gone: it served filler clips with no identity check, so any client who
# guessed a filename could read another user's audio. Clips are now served only
# by the identity-gated GET /api/clips/{filename} route in routes.py. The raw
# uploads dir is also not mounted — it held every user's full recordings with
# no path guard.
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.clips_dir).mkdir(parents=True, exist_ok=True)
