"""
Build FAISS vector index from medical knowledge base documents.

Reads all text/markdown files from the knowledge base directory,
splits them into chunks, embeds them, and builds the FAISS index.

Usage:
    python -m ml.scripts.build_vector_index
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def load_documents(kb_path: str = "ml/data/knowledge_base") -> list[dict[str, str]]:
    """Load and chunk documents from the knowledge base directory."""
    kb_dir = Path(kb_path)
    documents: list[dict[str, str]] = []

    if not kb_dir.exists():
        logger.warning("Knowledge base directory not found: %s", kb_path)
        return documents

    for file_path in kb_dir.glob("**/*"):
        if file_path.suffix.lower() in (".txt", ".md", ".text"):
            try:
                content = file_path.read_text(encoding="utf-8")
                # Simple chunking by paragraphs (production: use langchain splitters)
                chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 50]
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "title": f"{file_path.stem} (chunk {i+1})",
                        "content": chunk,
                    })
            except Exception as e:
                logger.error("Failed to read %s: %s", file_path, e)

    logger.info("Loaded %d document chunks from %s", len(documents), kb_path)
    return documents


def build() -> None:
    """Build and save the FAISS index."""
    from src.services.rag.vector_store import build_index, save_index

    documents = load_documents()

    if not documents:
        # Use sample medical knowledge if no documents are available
        documents = [
            {"title": "Diabetes Overview", "content": (
                "Diabetes is a chronic disease that occurs when the pancreas cannot produce "
                "enough insulin or when the body cannot effectively use the insulin it produces. "
                "Type 1 diabetes requires daily insulin administration. Type 2 diabetes can often "
                "be managed with lifestyle changes and oral medications."
            )},
            {"title": "Hypertension", "content": (
                "Hypertension or high blood pressure is a condition in which the blood vessels "
                "have persistently raised pressure. Normal blood pressure is 120/80 mmHg. "
                "It is a major risk factor for heart disease, stroke, and kidney failure."
            )},
            {"title": "Heart Disease Prevention", "content": (
                "Heart disease prevention involves maintaining a healthy lifestyle including "
                "regular physical activity, a balanced diet low in saturated fats and sodium, "
                "not smoking, limiting alcohol, managing stress, and regular health screenings."
            )},
            {"title": "Common Cold vs Flu", "content": (
                "The common cold and influenza are both respiratory illnesses with similar symptoms. "
                "The flu tends to be more severe with high fever, body aches, and fatigue. "
                "Colds are generally milder with runny nose, congestion, and sore throat."
            )},
            {"title": "Mental Health Basics", "content": (
                "Mental health includes emotional, psychological, and social well-being. "
                "Common conditions include depression, anxiety disorders, and PTSD. "
                "Treatment options include therapy, medication, and lifestyle modifications."
            )},
        ]
        logger.info("Using sample medical knowledge (%d documents)", len(documents))

    build_index(documents)
    save_index()
    logger.info("FAISS index built and saved successfully")


if __name__ == "__main__":
    build()
