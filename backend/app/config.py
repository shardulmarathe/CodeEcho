from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM API key — Google AIza... or Stanford llm.stanford.edu sk-...
    gemini_api_key: str = ""

    # Stanford llm.stanford.edu proxy (Gemini REST API format)
    google_gemini_base_url: str = ""

    # UIT AI API Gateway (OpenAI-compatible) — only if you have a UIT gateway key
    llm_base_url: str = ""

    @field_validator("gemini_api_key", "google_gemini_base_url", "llm_base_url", mode="before")
    @classmethod
    def strip_str_fields(cls, v: object) -> str:
        return str(v or "").strip()

    # Budget caps (USD). All reset at UTC midnight (see services/budget.py).
    # api_budget_cap_usd is the GLOBAL DAILY ceiling on estimated LLM spend across
    # everyone. The per-subject caps stop one user / guest-IP from draining it:
    # signed-in users get user_daily_cap_usd, guests/anon get guest_daily_cap_usd.
    api_budget_cap_usd: float = 3.0
    user_daily_cap_usd: float = 0.50   # per signed-in Clerk user, per day
    guest_daily_cap_usd: float = 0.15  # per guest / anonymous IP, per day

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "audio"

    # Clerk auth — backend verifies session JWTs via Clerk's JWKS (RS256).
    # clerk_issuer is your Clerk Frontend API origin, e.g. https://your-app.clerk.accounts.dev
    clerk_issuer: str = ""
    clerk_jwks_url: str = ""  # defaults to {issuer}/.well-known/jwks.json when blank
    clerk_secret_key: str = ""  # optional, only needed for Clerk Backend API calls

    @property
    def effective_clerk_jwks_url(self) -> str:
        if self.clerk_jwks_url:
            return self.clerk_jwks_url
        if self.clerk_issuer:
            return self.clerk_issuer.rstrip("/") + "/.well-known/jwks.json"
        return ""

    # Rate limiting (slowapi) — per client IP
    rate_limit_default: str = "120/minute"
    rate_limit_expensive: str = "10/minute"  # upload / analyze / score / generate

    # Local storage fallback
    upload_dir: str = "./uploads"
    clips_dir: str = "./clips"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Model for text analysis (fillers, transitions, debug tests)
    gemini_model: str = "gemini-2.5-flash"

    # Model for audio transcription
    gemini_transcription_model: str = "gemini-2.5-flash"

    @property
    def effective_transcription_model(self) -> str:
        return self.gemini_transcription_model.strip() or self.gemini_model

    # --- RAG / embeddings ---
    # The Stanford gateway exposes no embedding model, so by default we embed locally
    # (offline, free) via fastembed. Set embedding_api_key to a Google AIza key to use
    # Gemini gemini-embedding-001 instead. Both are 768-dim to match kb_documents.embedding.
    embedding_local_model: str = "BAAI/bge-base-en-v1.5"  # 768-dim, ONNX, offline
    embedding_model: str = "gemini-embedding-001"  # used only with a Google-direct key
    embedding_api_key: str = ""  # Google AIza key; blank => local embeddings
    embedding_base_url: str = "https://generativelanguage.googleapis.com"
    embedding_dimension: int = 768
    kb_top_k: int = 4  # guidance chunks fed to the scorer per answer
    # Local RAG loads a ~300MB ONNX embedding model. Disable on memory-constrained hosts
    # (Render free tier). Scoring still works; reference coaching blocks are omitted.
    # Re-enable with EMBEDDING_API_KEY (Google) or more RAM.
    rag_enabled: bool = True
    # Reranker: a local cross-encoder reorders the hybrid candidates for precision.
    # Retrieve `rerank_pool`, rerank, keep `kb_top_k`. Offline via fastembed (no API cost).
    rerank_enabled: bool = True
    rerank_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"
    rerank_pool: int = 20  # hybrid candidates fetched before reranking down to kb_top_k

    # Audio limits
    # Hard cap on a single answer (1:30) — mirrors a typical interview answer length
    # and bounds transcription cost. Enforced in the analysis pipeline before any paid
    # work; the recorder UI also auto-stops at this limit.
    max_audio_duration_sec: int = 90
    clip_padding_sec: float = 3.0

    # Debug routes (Gemini smoke test). OFF by default — they are unauthenticated and
    # let anyone spend your LLM budget. Set ENABLE_DEBUG_ROUTES=true in local .env only.
    enable_debug_routes: bool = False


settings = Settings()
