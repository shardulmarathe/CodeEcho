"""Ingest behavioral-interview guidance PDFs into the RAG knowledge base.

Usage (from the backend/ directory, venv active):
    python -m scripts.ingest_kb <pdf-folder> [--bucket experience|project|introspection|learning]
    python -m scripts.ingest_kb data/kb_sources
    python -m scripts.ingest_kb data/kb_sources --bucket introspection --reset

Each PDF is parsed (pypdf), split into ~250-word overlapping chunks, embedded, and stored
via kb_store (Supabase pgvector if configured, else the local data/kb_index.json index).
Drop your PDFs in a folder and point this at it. --bucket tags every chunk so the scorer can
prefer same-bucket guidance; omit it for general guides and retrieval falls back to semantic
similarity across the whole corpus.
"""

import argparse
import sys
import uuid
from pathlib import Path

from app.models import KBDocument
from app.services import kb_store
from app.services.embeddings import active_model_name, embed_batch
from app.services.kb_store import INDEX_PATH, delete_bucket

CHUNK_WORDS = 250
CHUNK_OVERLAP = 40


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _chunk(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, CHUNK_WORDS - CHUNK_OVERLAP)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + CHUNK_WORDS]).strip()
        if len(chunk) > 40:  # skip near-empty tails
            chunks.append(chunk)
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest behavioral guidance PDFs into the RAG KB.")
    parser.add_argument("folder", help="Folder containing .pdf files")
    parser.add_argument("--bucket", default=None, help="Tag all chunks with a behavioral bucket")
    parser.add_argument("--reset", action="store_true", help="Clear the local index before ingesting")
    parser.add_argument(
        "--replace-bucket",
        action="store_true",
        help="Delete existing Supabase chunks for --bucket before ingesting",
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1

    if args.reset and INDEX_PATH.exists():
        INDEX_PATH.unlink()
        print(f"Cleared local index {INDEX_PATH}")

    if args.replace_bucket and args.bucket:
        removed = delete_bucket(args.bucket)
        if removed:
            print(f"Cleared {removed} existing chunks for bucket={args.bucket}")

    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {folder}", file=sys.stderr)
        return 1

    print(f"Embedding with {active_model_name()}")
    total = 0
    for pdf in pdfs:
        text = _read_pdf(pdf)
        chunks = _chunk(text)
        if not chunks:
            print(f"  {pdf.name}: no extractable text, skipped")
            continue
        vectors = embed_batch(chunks)
        docs = [
            KBDocument(
                id=str(uuid.uuid4()),
                kind="behavioral_guidance",
                ref=pdf.name,
                content=chunk,
                embedding=vec,
                meta={"source": pdf.name, "bucket": args.bucket, "chunk": i},
            )
            for i, (chunk, vec) in enumerate(zip(chunks, vectors))
        ]
        kb_store.upsert_docs(docs)
        total += len(docs)
        print(f"  {pdf.name}: {len(docs)} chunks")

    print(f"Done. {total} chunks ingested. KB now holds {kb_store.count()} chunks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
