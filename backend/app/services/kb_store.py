"""Knowledge-base store for RAG guidance chunks (the `kb_documents` corpus).

Mirrors `store.py`: durable Supabase + pgvector when configured, else a local on-disk
JSON index with in-memory cosine. The ingest script writes here; behavioral scoring reads
via `retrieve_similar`. Everything degrades gracefully — a missing/empty corpus or an
embedding failure yields `[]`, and scoring behaves exactly as it did before RAG.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models import KBDocument
from app.services import supabase_client
from app.services.embeddings import active_model_name, embed_text

INDEX_PATH = Path("./data/kb_index.json")
_lock = threading.Lock()
_mem_index: Optional[dict] = None  # {"model": str, "docs": [ {id, content, embedding, meta, ...} ]}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- local index
def _load_index() -> dict:
    global _mem_index
    if _mem_index is None:
        if INDEX_PATH.exists():
            try:
                _mem_index = json.loads(INDEX_PATH.read_text())
            except Exception:
                _mem_index = {"model": active_model_name(), "docs": []}
        else:
            _mem_index = {"model": active_model_name(), "docs": []}
    return _mem_index


def _save_index(idx: dict) -> None:
    global _mem_index
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(idx))
    _mem_index = idx


def _cosine_topk(query_vec: list[float], docs: list[dict], k: int) -> list[tuple[dict, float]]:
    if not docs:
        return []
    import numpy as np

    matrix = np.array([d["embedding"] for d in docs], dtype=float)
    q = np.array(query_vec, dtype=float)
    q = q / (np.linalg.norm(q) or 1.0)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / (norms + 1e-9)
    sims = matrix @ q
    order = np.argsort(-sims)[:k]
    return [(docs[i], float(sims[i])) for i in order]


# --------------------------------------------------------------------------- hybrid fusion
def _dense_order(query_vec: list[float], docs: list[dict], k: int) -> list[int]:
    """Indices of `docs` ranked by cosine similarity to the query (best first)."""
    if not docs:
        return []
    import numpy as np

    matrix = np.array([d["embedding"] for d in docs], dtype=float)
    q = np.array(query_vec, dtype=float)
    q = q / (np.linalg.norm(q) or 1.0)
    matrix = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-9)
    return list(np.argsort(-(matrix @ q))[:k])


def _lexical_order(query: str, docs: list[dict], k: int) -> list[int]:
    """Indices of `docs` ranked by simple keyword-overlap (term frequency), best first.

    A lightweight local stand-in for Postgres full-text search — good enough for the
    small on-disk fallback index; Supabase uses real ts_rank via the hybrid RPC."""
    import re

    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    if not terms:
        return []
    scored: list[tuple[int, int]] = []
    for i, d in enumerate(docs):
        content = (d.get("content") or "").lower()
        score = sum(content.count(t) for t in terms)
        if score > 0:
            scored.append((i, score))
    scored.sort(key=lambda x: -x[1])
    return [i for i, _ in scored[:k]]


def _rrf_fuse(orders: list[list[int]], k: int, rrf_k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion: combine several ranked index lists into one top-k."""
    scores: dict[int, float] = {}
    for order in orders:
        for rank, idx in enumerate(order):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)
    return sorted(scores, key=lambda i: -scores[i])[:k]


# --------------------------------------------------------------------------- public API
def upsert_docs(docs: list[KBDocument]) -> int:
    """Persist guidance chunks. Returns how many were written."""
    if not docs:
        return 0

    if supabase_client.is_configured():
        try:
            rows = [
                {
                    "id": d.id,
                    "kind": d.kind,
                    "ref": d.ref,
                    "content": d.content,
                    "embedding": d.embedding,
                    "meta": d.meta,
                }
                for d in docs
            ]
            supabase_client.get_client().table("kb_documents").upsert(rows).execute()
            return len(docs)
        except Exception:
            pass  # fall through to local index

    with _lock:
        idx = _load_index()
        idx["model"] = active_model_name()
        idx["docs"].extend(d.model_dump() for d in docs)
        _save_index(idx)
    return len(docs)


def count() -> int:
    """Number of stored chunks (best-effort)."""
    if supabase_client.is_configured():
        try:
            res = (
                supabase_client.get_client()
                .table("kb_documents")
                .select("id", count="exact")
                .execute()
            )
            return res.count or 0
        except Exception:
            pass
    return len(_load_index()["docs"])


def _rows_to_docs(rows: list[dict]) -> list[KBDocument]:
    return [
        KBDocument(
            id=str(r.get("id")),
            kind=r.get("kind", "behavioral_guidance"),
            ref=r.get("ref"),
            content=r.get("content", ""),
            meta=r.get("meta") or {},
        )
        for r in rows
    ]


def _retrieve_supabase(
    query_vec: list[float], query_text: str, top_k: int, bucket: Optional[str]
) -> Optional[list[KBDocument]]:
    """HYBRID retrieval: dense pgvector + Postgres full-text, fused with RRF in SQL via the
    `match_kb_documents_hybrid` RPC. Falls back to the dense-only `match_kb_documents` RPC
    if the hybrid function isn't present yet (migration not applied); returns None only if
    both fail, so the caller can use the local index.

    Strict bucket filter: a bucketed query is restricted to that bucket and nothing else,
    so coding/behavioral/system_design standards never cross-contaminate."""
    client = supabase_client.get_client()
    try:
        rows = (
            client.rpc(
                "match_kb_documents_hybrid",
                {
                    "query_embedding": query_vec,
                    "query_text": query_text,
                    "match_count": top_k,
                    "filter_kind": None,
                    "filter_bucket": bucket,
                },
            )
            .execute()
            .data
            or []
        )
        return _rows_to_docs(rows)
    except Exception:
        pass
    # Fallback: dense-only RPC (works before the hybrid migration is applied).
    try:
        rows = (
            client.rpc(
                "match_kb_documents",
                {
                    "query_embedding": query_vec,
                    "match_count": top_k,
                    "filter_kind": None,
                    "filter_bucket": bucket,
                },
            )
            .execute()
            .data
            or []
        )
        return _rows_to_docs(rows)
    except Exception:
        return None


def _retrieve_local(
    query_vec: list[float], query_text: str, top_k: int, bucket: Optional[str]
) -> list[KBDocument]:
    """HYBRID retrieval over the on-disk index: dense cosine + keyword overlap, RRF-fused.

    Strict bucket filter (mirrors _retrieve_supabase)."""
    docs = _load_index()["docs"]
    if bucket:
        docs = [d for d in docs if (d.get("meta") or {}).get("bucket") == bucket]
    if not docs:
        return []
    pool = max(top_k * 5, 20)
    dense = _dense_order(query_vec, docs, pool)
    sparse = _lexical_order(query_text, docs, pool)
    fused = _rrf_fuse([dense, sparse], top_k) if sparse else dense[:top_k]
    return [
        KBDocument(
            id=str(docs[i].get("id", "")),
            kind=docs[i].get("kind", "behavioral_guidance"),
            ref=docs[i].get("ref"),
            content=docs[i].get("content", ""),
            meta=docs[i].get("meta") or {},
        )
        for i in fused
    ]


def retrieve_similar(
    query: str, top_k: Optional[int] = None, bucket: Optional[str] = None
) -> list[KBDocument]:
    """Top-k guidance chunks for `query`: hybrid (dense + keyword) retrieval, then a
    cross-encoder rerank down to top_k. Empty on failure."""
    from app.services import reranker  # local import avoids a heavy import at module load

    top_k = top_k or settings.kb_top_k
    query_vec = embed_text(query)
    if query_vec is None:
        return []
    # When reranking, pull a larger high-recall pool and let the cross-encoder pick the best.
    fetch_k = max(settings.rerank_pool, top_k) if reranker.is_enabled() else top_k

    docs: Optional[list[KBDocument]] = None
    if supabase_client.is_configured():
        docs = _retrieve_supabase(query_vec, query, fetch_k, bucket)
    if docs is None:
        docs = _retrieve_local(query_vec, query, fetch_k, bucket)

    return reranker.rerank(query, docs, top_k)
