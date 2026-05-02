"""
FAISS vector store for medical knowledge retrieval.

Manages document embedding, indexing, and similarity search
using sentence-transformers and FAISS.
"""

from pathlib import Path
from typing import Any

import numpy as np

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_index: Any = None
_documents: list[dict[str, str]] = []
_embedding_model: Any = None


def _get_embedding_model() -> Any:
    """Lazy-load the sentence transformer embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        settings = get_settings()
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        logger.info("embedding_model_loaded", model=settings.EMBEDDING_MODEL_NAME)
    return _embedding_model


def build_index(documents: list[dict[str, str]]) -> None:
    """
    Build FAISS index from documents.

    Args:
        documents: List of dicts with 'title' and 'content' keys.
    """
    global _index, _documents
    import faiss

    model = _get_embedding_model()
    texts = [doc["content"] for doc in documents]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    dimension = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
    _index.add(embeddings)
    _documents = documents

    logger.info("faiss_index_built", num_documents=len(documents), dimension=dimension)


def save_index(path: str | None = None) -> None:
    """Save FAISS index to disk."""
    import json

    import faiss

    if _index is None:
        raise RuntimeError("No index to save — call build_index first")

    settings = get_settings()
    save_path = Path(path or settings.FAISS_INDEX_PATH)
    save_path.mkdir(parents=True, exist_ok=True)

    faiss.write_index(_index, str(save_path / "index.faiss"))
    with open(save_path / "documents.json", "w") as f:
        json.dump(_documents, f)

    logger.info("faiss_index_saved", path=str(save_path))


def load_index(path: str | None = None) -> bool:
    """Load FAISS index from disk. Returns True if successful."""
    global _index, _documents
    import json

    import faiss

    settings = get_settings()
    load_path = Path(path or settings.FAISS_INDEX_PATH)
    index_file = load_path / "index.faiss"
    docs_file = load_path / "documents.json"

    if not index_file.exists() or not docs_file.exists():
        logger.warning("faiss_index_not_found", path=str(load_path))
        return False

    _index = faiss.read_index(str(index_file))
    with open(docs_file) as f:
        _documents = json.load(f)

    logger.info("faiss_index_loaded", num_documents=len(_documents))
    return True


def search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    Search for documents similar to the query.

    Returns list of dicts with 'title', 'content', and 'score'.
    """
    if _index is None or not _documents:
        logger.warning("search_called_without_index")
        return []

    model = _get_embedding_model()
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding, dtype=np.float32)

    scores, indices = _index.search(query_embedding, min(top_k, len(_documents)))

    results = []
    for score, idx in zip(scores[0], indices[0], strict=False):
        if idx >= 0 and idx < len(_documents):
            results.append({
                "title": _documents[idx].get("title", "Unknown"),
                "content": _documents[idx]["content"],
                "score": float(score),
            })

    return results
