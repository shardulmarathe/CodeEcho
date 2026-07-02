"""Cross-encoder reranker — stage 2 of retrieval.

Hybrid retrieval (dense + keyword) gets a high-recall shortlist cheaply; this reorders
that shortlist with a cross-encoder that reads each (query, chunk) PAIR together, which
is far more precise about true relevance. Runs LOCALLY and offline via fastembed (same
stack as embeddings — no API cost). Degrades gracefully: any failure returns the input
order unchanged, so retrieval never breaks because of the reranker.
"""

import threading
from typing import Optional

from app.config import settings
from app.models import KBDocument

_lock = threading.Lock()
_model = None  # lazily constructed fastembed TextCrossEncoder


def is_enabled() -> bool:
    return settings.rerank_enabled


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from fastembed.rerank.cross_encoder import TextCrossEncoder  # heavy, deferred

                _model = TextCrossEncoder(settings.rerank_model)
    return _model


def rerank(query: str, docs: list[KBDocument], top_k: int) -> list[KBDocument]:
    """Reorder `docs` by cross-encoder relevance to `query`, keeping the best `top_k`.

    On any failure (model unavailable, empty input) returns the first `top_k` unchanged.
    """
    if not settings.rerank_enabled or len(docs) <= 1:
        return docs[:top_k]
    try:
        model = _get_model()
        scores = list(model.rerank(query, [d.content for d in docs]))
        ranked = sorted(zip(docs, scores), key=lambda pair: -pair[1])
        return [d for d, _ in ranked[:top_k]]
    except Exception:
        return docs[:top_k]
