"""Text embeddings for RAG.

The Stanford LLM gateway exposes no embedding model, so embeddings do NOT route through
`llm_client`. Three backends (all 768-dim to match `kb_documents.embedding`):
  - **azure** (preferred): `text-embedding-3-small` via Azure OpenAI when AZURE_OPENAI_* set
  - **google**: `gemini-embedding-001` when `EMBEDDING_API_KEY` is set
  - **local** (default): fastembed `BAAI/bge-base-en-v1.5`, offline, free

Ingest and query MUST use the same backend (vectors share one space).
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
    if settings.azure_embeddings_configured:
        return f"azure:{settings.azure_openai_embedding_deployment}"
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


def _request_with_retry(client: httpx.Client, method: str, url: str, **kwargs) -> httpx.Response:
    for attempt in range(12):
        resp = client.request(method, url, **kwargs)
        if resp.status_code in (429, 503) and attempt < 11:
            time.sleep(min(2**attempt + 1, 90))
            continue
        resp.raise_for_status()
        return resp
    raise RuntimeError("unreachable")


def _embed_azure(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    base = settings.azure_openai_endpoint.rstrip("/")
    deployment = settings.azure_openai_embedding_deployment
    url = (
        f"{base}/openai/deployments/{deployment}/embeddings"
        f"?api-version={settings.azure_openai_api_version}"
    )
    headers = {"api-key": settings.azure_openai_api_key}
    out: list[list[float]] = []
    batch_size = 100

    with httpx.Client(timeout=120.0) as client:
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            payload: dict = {"input": chunk}
            if settings.embedding_dimension:
                payload["dimensions"] = settings.embedding_dimension
            resp = _request_with_retry(client, "POST", url, headers=headers, json=payload)
            data = resp.json().get("data", [])
            # Azure returns one object per input, each with an index field.
            data.sort(key=lambda row: row.get("index", 0))
            for row in data:
                out.append([float(x) for x in row["embedding"]])
            if len(chunk) > 1:
                time.sleep(0.5)

    tokens = sum(int(len(t.split()) * 1.3) for t in texts)
    try:
        record_cost("azure-embeddings", f"Embed {len(texts)} texts", estimate_embedding_cost(tokens))
    except Exception:
        pass
    return out


def _embed_google(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    base = settings.embedding_base_url.rstrip("/")
    model = settings.embedding_model
    single_url = f"{base}/v1beta/models/{model}:embedContent"
    batch_url = f"{base}/v1beta/models/{model}:batchEmbedContents"
    out: list[list[float]] = []
    batch_size = 8

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
            resp = _request_with_retry(
                client,
                "POST",
                single_url,
                params={"key": settings.embedding_api_key},
                json=_request_payload(texts[0]),
            )
            out.append([float(x) for x in resp.json()["embedding"]["values"]])
        else:
            for start in range(0, len(texts), batch_size):
                chunk = texts[start : start + batch_size]
                resp = _request_with_retry(
                    client,
                    "POST",
                    batch_url,
                    params={"key": settings.embedding_api_key},
                    json={"requests": [_request_payload(text) for text in chunk]},
                )
                for emb in resp.json().get("embeddings", []):
                    out.append([float(x) for x in emb["values"]])
                time.sleep(2.5)

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
    if settings.azure_embeddings_configured:
        return _embed_azure(texts)
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
