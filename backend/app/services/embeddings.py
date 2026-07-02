"""Text embeddings for RAG.

The Stanford LLM gateway exposes no embedding model, so embeddings do NOT route through
`llm_client`. Two backends:
  - **local** (default): fastembed `BAAI/bge-base-en-v1.5`, 768-dim, offline, free.
  - **google**: Gemini `gemini-embedding-001` via `:embedContent`, used only when
    `settings.embedding_api_key` (a Google AIza key) is set.

Both are 768-dim to match `kb_documents.embedding`. Ingest and query MUST use the same
backend (vectors share one space); `active_model_name()` is stamped into the index so a
mismatch is detectable. Local cost is $0; the Google path is budget-tracked.
"""

import threading
import time
from typing import Optional

import httpx

from app.config import settings
from app.services.budget import estimate_embedding_cost, record_cost

_lock = threading.Lock()
_local_model = None  # lazily constructed fastembed model


def active_model_name() -> str:
    """Identifier for the embedding space currently in use (stored with the index)."""
    if settings.embedding_api_key:
        return f"google:{settings.embedding_model}"
    return f"local:{settings.embedding_local_model}"


def _get_local():
    global _local_model
    if _local_model is None:
        with _lock:
            if _local_model is None:
                from fastembed import TextEmbedding  # heavy import, deferred

                _local_model = TextEmbedding(settings.embedding_local_model)
    return _local_model


def _embed_google(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    base = settings.embedding_base_url.rstrip("/")
    model = settings.embedding_model
    single_url = f"{base}/v1beta/models/{model}:embedContent"
    batch_url = f"{base}/v1beta/models/{model}:batchEmbedContents"
    out: list[list[float]] = []
    batch_size = 8

    def _request(client: httpx.Client, url: str, payload: dict) -> httpx.Response:
        for attempt in range(12):
            resp = client.post(
                url,
                params={"key": settings.embedding_api_key},
                json=payload,
            )
            if resp.status_code in (429, 503) and attempt < 11:
                time.sleep(min(2**attempt + 1, 90))
                continue
            resp.raise_for_status()
            return resp
        raise RuntimeError("unreachable")

    def _request_payload(text: str) -> dict:
        payload: dict = {
            "model": f"models/{model}",
            "content": {"parts": [{"text": text}]},
        }
        if settings.embedding_dimension:
            payload["outputDimensionality"] = settings.embedding_dimension
        return payload

    with httpx.Client(timeout=120.0) as client:
        if len(texts) == 1:
            resp = _request(client, single_url, _request_payload(texts[0]))
            out.append([float(x) for x in resp.json()["embedding"]["values"]])
        else:
            for start in range(0, len(texts), batch_size):
                chunk = texts[start : start + batch_size]
                resp = _request(
                    client,
                    batch_url,
                    {"requests": [_request_payload(text) for text in chunk]},
                )
                for emb in resp.json().get("embeddings", []):
                    out.append([float(x) for x in emb["values"]])
                time.sleep(2.5)
    # Rough token estimate for the ledger (~1.3 tokens/word).
    tokens = sum(int(len(t.split()) * 1.3) for t in texts)
    try:
        record_cost("google-embeddings", f"Embed {len(texts)} texts", estimate_embedding_cost(tokens))
    except Exception:
        pass
    return out


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into 768-dim vectors. Empty input -> empty list."""
    texts = [t for t in texts]
    if not texts:
        return []
    if settings.embedding_api_key:
        return _embed_google(texts)
    model = _get_local()
    return [[float(x) for x in vec] for vec in model.embed(list(texts))]


def embed_text(text: str) -> Optional[list[float]]:
    """Embed a single string; returns None on failure so callers can degrade gracefully."""
    try:
        vecs = embed_batch([text])
        return vecs[0] if vecs else None
    except Exception:
        return None
