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

    # LLM API key. Google AIza... or Stanford llm.stanford.edu sk-...
    gemini_api_key: str = ""

    # Stanford llm.stanford.edu proxy (Gemini REST API format)
    google_gemini_base_url: str = ""

    # UIT AI API Gateway (OpenAI-compatible), only if you have a UIT gateway key
    llm_base_url: str = ""

    @field_validator(
        "gemini_api_key",
        "google_gemini_base_url",
        "llm_base_url",
        "azure_openai_whisper_endpoint",
        "azure_openai_whisper_api_key",
        "azure_openai_whisper_deployment",
        "gemini_scoring_model",
        "supabase_jwt_secret",
        mode="before",
    )
    @classmethod
    def strip_str_fields(cls, v: object) -> str:
        return str(v or "").strip()

    # Budget caps (USD). All reset at UTC midnight (see services/budget.py).
    # Set any of these to 0 to disable that scope's limit entirely.
    #
    # The per-subject caps ship DISABLED. The upstream LLM key (Stanford proxy) has no
    # billing attached and Whisper runs on non-renewing student credit, so throttling an
    # individual user buys nothing that per-IP rate limiting doesn't already buy — it
    # just degrades the product for real users. Abuse is handled by rate_limit_expensive.
    #
    # api_budget_cap_usd stays ON as a circuit breaker: it bounds a runaway retry loop or
    # a misconfigured model, not any individual's usage. Raise it rather than zero it.
    api_budget_cap_usd: float = 25.0
    user_daily_cap_usd: float = 0.0   # 0 = unlimited per signed-in user
    guest_daily_cap_usd: float = 0.0  # 0 = unlimited per guest / anonymous IP

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "audio"

    # Optional. Only needed to verify legacy HS256 tokens. Current Supabase
    # projects sign with ECC and are verified via JWKS at SUPABASE_URL.
    supabase_jwt_secret: str = ""

    # Rate limiting (slowapi), per client IP
    rate_limit_default: str = "120/minute"
    rate_limit_expensive: str = "10/minute"  # upload / analyze / score / generate

    # Local storage fallback
    upload_dir: str = "./uploads"
    clips_dir: str = "./clips"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Model for fast text tasks (fillers, transitions, question generation, debug tests)
    gemini_model: str = "gemini-2.5-flash"

    # --- Answer scoring quality ---
    # Scoring is reasoning-heavy, unlike fillers/transitions (thinkingBudget:0 for speed),
    # scorecards run on pro with a real thinking budget for higher-quality rubric judgments.
    gemini_scoring_model: str = "gemini-2.5-pro"
    # >0 enables the model's reasoning pass; 0 disables it; <0 uses the model's own default.
    gemini_scoring_thinking_budget: int = 2048
    # Headroom so reasoning tokens don't starve the JSON scorecard output on the proxy.
    gemini_scoring_max_output_tokens: int = 12288

    @property
    def effective_scoring_model(self) -> str:
        return self.gemini_scoring_model.strip() or self.gemini_model

    # --- Azure OpenAI Whisper transcription (preferred STT when configured) ---
    # When set, audio is transcribed by Azure Whisper with native word-level timestamps.
    # Answer scoring stays on effective_scoring_model (pro by default).
    # Endpoint/key fall back to the shared AZURE_OPENAI_* embedding creds when blank,
    # so a single Azure resource can serve both. Word timestamps need api-version
    # >= 2024-06-01.
    azure_openai_whisper_deployment: str = ""  # e.g. "whisper"; blank disables Whisper STT
    azure_openai_whisper_endpoint: str = ""    # falls back to azure_openai_endpoint
    azure_openai_whisper_api_key: str = ""     # falls back to azure_openai_api_key
    azure_openai_whisper_api_version: str = "2024-06-01"

    @property
    def whisper_endpoint(self) -> str:
        return (self.azure_openai_whisper_endpoint or self.azure_openai_endpoint).rstrip("/")

    @property
    def whisper_api_key(self) -> str:
        return self.azure_openai_whisper_api_key or self.azure_openai_api_key

    @property
    def whisper_configured(self) -> bool:
        return bool(
            self.whisper_endpoint
            and self.whisper_api_key
            and self.azure_openai_whisper_deployment
        )

    @property
    def transcription_configured(self) -> bool:
        """True when Azure Whisper STT is configured."""
        return self.whisper_configured

    # --- RAG / embeddings ---
    # The Stanford gateway exposes no embedding model. Three backends (pick one via env):
    #   - azure: text-embedding-3-small @ 768-dim (AZURE_OPENAI_* vars)
    #   - google: gemini-embedding-001 @ 768-dim (EMBEDDING_API_KEY)
    #   - local: fastembed BAAI/bge-base-en-v1.5 (offline; OOM on Render free tier)
    # Ingest and query MUST use the same backend.
    embedding_local_model: str = "BAAI/bge-base-en-v1.5"  # 768-dim, ONNX, offline
    embedding_model: str = "gemini-embedding-001"  # Google-only
    embedding_api_key: str = ""  # Google key; blank unless using Google backend
    embedding_base_url: str = "https://generativelanguage.googleapis.com"
    embedding_dimension: int = 768
    # Azure OpenAI embeddings (preferred for bulk ingest, higher rate limits than Google free tier)
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2024-02-01"
    kb_top_k: int = 6  # guidance chunks fed to the scorer per answer
    # Local RAG loads a ~300MB ONNX embedding model. Disable on memory-constrained hosts
    # (Render free tier). Scoring still works; reference coaching blocks are omitted.
    # Re-enable with Azure or Google cloud embeddings (no local ONNX load).
    rag_enabled: bool = True
    # Reranker: a local cross-encoder reorders the hybrid candidates for precision.
    # Retrieve `rerank_pool`, rerank, keep `kb_top_k`. Offline via fastembed (no API cost).
    rerank_enabled: bool = True
    rerank_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"
    rerank_pool: int = 20  # hybrid candidates fetched before reranking down to kb_top_k

    # Absolute ceiling on a single answer. Per-attempt cap lives on
    # SessionResult.max_duration_sec (3 min behavioral/coding, 5 min project/design).
    max_audio_duration_sec: int = 300
    clip_padding_sec: float = 3.0

    # Debug routes (Gemini smoke test). OFF by default, they are unauthenticated and
    # let anyone spend your LLM budget. Set ENABLE_DEBUG_ROUTES=true in local .env only.
    enable_debug_routes: bool = False

    @property
    def azure_embeddings_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_embedding_deployment
        )

    @property
    def cloud_embeddings_configured(self) -> bool:
        return self.azure_embeddings_configured or bool(self.embedding_api_key)


settings = Settings()
