"""
Build FAISS vector index from medical knowledge base documents.

Ingests all PDF, TXT, and MD files from the knowledge base directory,
chunks them, generates embeddings via Gemini, and saves a FAISS index.

Usage:
    python -m ml.scripts.build_vector_index
"""

import os
import sys
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


#  Configuration 
KNOWLEDGE_BASE_DIR = Path("ml/data/knowledge_base")
FAISS_INDEX_PATH = Path("ml/models/faiss_index")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "models/embedding-001"


#  Loader Mapping 
LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
}


def discover_documents(directory: Path) -> list[Path]:
    """Find all supported document files in the knowledge base."""
    supported_extensions = set(LOADER_MAP.keys())
    files = []
    for file_path in directory.rglob("*"):
        if file_path.suffix.lower() in supported_extensions:
            files.append(file_path)
    return sorted(files)


def load_and_chunk_documents(file_paths: list[Path]) -> list:
    """Load documents and split into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks = []
    for file_path in file_paths:
        loader_class = LOADER_MAP.get(file_path.suffix.lower())
        if loader_class is None:
            print(f"  ⚠ Skipping unsupported file: {file_path}")
            continue

        print(f"  📄 Loading: {file_path.name}")
        try:
            loader = loader_class(str(file_path))
            documents = loader.load()
            chunks = text_splitter.split_documents(documents)
            all_chunks.extend(chunks)
            print(f"     → {len(chunks)} chunks extracted")
        except Exception as e:
            print(f"  ❌ Error loading {file_path.name}: {e}")

    return all_chunks


def build_faiss_index(chunks: list, output_path: Path) -> None:
    """Generate embeddings and build the FAISS vector store."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable is not set.")
        print("   Set it with:  set GOOGLE_API_KEY=your_key_here  (Windows)")
        print("   Or:           export GOOGLE_API_KEY=your_key_here  (Linux/Mac)")
        sys.exit(1)

    print(f"\n🔗 Generating embeddings with Gemini ({EMBEDDING_MODEL})...")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    print("📦 Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vectorstore.save_local(str(output_path))
    print(f"✅ FAISS index saved to: {output_path}")


def main() -> None:
    """Main entry point for building the vector index."""
    print("=" * 60)
    print("🏥 Health Intelligence — FAISS Vector Index Builder")
    print("=" * 60)

    # Check knowledge base directory
    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"\n❌ Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        sys.exit(1)

    # Discover files
    print(f"\n📂 Scanning: {KNOWLEDGE_BASE_DIR}")
    files = discover_documents(KNOWLEDGE_BASE_DIR)

    if not files:
        print("\n⚠ No supported files found in the knowledge base directory.")
        print(f"  Place PDF, TXT, or MD files in: {KNOWLEDGE_BASE_DIR}")
        print("  Supported formats: .pdf, .txt, .md")
        sys.exit(1)

    print(f"   Found {len(files)} document(s):\n")
    for f in files:
        print(f"   • {f.name} ({f.stat().st_size / 1024:.1f} KB)")

    # Load and chunk
    print("\n📝 Loading and chunking documents...")
    chunks = load_and_chunk_documents(files)

    if not chunks:
        print("\n❌ No text chunks were extracted. Check your documents.")
        sys.exit(1)

    print(f"\n📊 Total chunks: {len(chunks)}")

    # Build index
    build_faiss_index(chunks, FAISS_INDEX_PATH)

    print("\n" + "=" * 60)
    print("🎉 Vector index built successfully!")
    print(f"   Documents: {len(files)}")
    print(f"   Chunks:    {len(chunks)}")
    print(f"   Index:     {FAISS_INDEX_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
