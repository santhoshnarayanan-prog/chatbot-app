"""
RAG knowledge service.
Handles: document parsing, website crawling, chunking, embeddings, ChromaDB storage and retrieval.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Lazy-loaded singletons ─────────────────────────────────────────────────────
_chroma_client = None
_collection = None
_CHROMA_DB_PATH = Path(__file__).resolve().parents[2] / "chroma_db"
_embedder = None


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        _CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(_CHROMA_DB_PATH))
        _collection = _chroma_client.get_or_create_collection(
            "knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection ready (%d chunks)", _collection.count())
    return _collection


def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise RuntimeError(
                "Failed to load the local embedding model. "
                "Install matching versions of torch and numpy, or ensure the environment supports sentence-transformers. "
                f"Original error: {e}"
            ) from e

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")
    return _embedder


# ── Text chunking ──────────────────────────────────────────────────────────────

def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk.strip()) > 30:   # skip near-empty chunks
            chunks.append(chunk)
    return chunks


# ── Vector store operations ────────────────────────────────────────────────────

def add_to_knowledge_base(
    content: str,
    source_id: int,
    source_name: str,
    source_type: str,
) -> int:
    """Chunk → embed → store. Returns number of chunks added."""
    chunks = _chunk_text(content)
    if not chunks:
        return 0

    collection = _get_collection()
    embedder = _get_embedder()

    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
    ids = [f"src_{source_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source_id": str(source_id), "source_name": source_name, "type": source_type}
        for _ in chunks
    ]

    collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    logger.info("Stored %d chunks from '%s'", len(chunks), source_name)
    return len(chunks)


def query_knowledge(question: str, n_results: int = 4) -> str:
    """Return the most relevant context passages for a question, or '' if none."""
    try:
        collection = _get_collection()
        total = collection.count()
        if total == 0:
            return ""

        embedder = _get_embedder()
        query_emb = embedder.encode([question], show_progress_bar=False).tolist()

        results = collection.query(
            query_embeddings=query_emb,
            n_results=min(n_results, total),
        )
        docs = results.get("documents", [[]])[0]
        return "\n\n---\n\n".join(docs) if docs else ""
    except Exception as e:
        logger.error("Knowledge query failed: %s", e)
        return ""


def delete_source_chunks(source_id: int) -> None:
    """Remove all ChromaDB chunks that belong to a source."""
    try:
        collection = _get_collection()
        results = collection.get(where={"source_id": str(source_id)})
        if results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info("Deleted %d chunks for source_id=%d", len(results["ids"]), source_id)
    except Exception as e:
        logger.error("Failed to delete chunks for source %d: %s", source_id, e)


# ── Parsers ────────────────────────────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> str:
    from io import BytesIO
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(file_bytes))
    pages = [p.extract_text() for p in reader.pages if p.extract_text()]
    return "\n".join(pages)


def parse_docx(file_bytes: bytes) -> str:
    from io import BytesIO
    import docx
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


# ── Website crawler ────────────────────────────────────────────────────────────

def crawl_website(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MCUBEBot/1.0)"},
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 20]
    return "\n".join(lines)
