"""
Gemini-powered Medical RAG Pipeline.

Pipeline stages:
  1. Document Ingestion: PDF → chunks → Gemini embeddings → FAISS
  2. Retrieval: Query → FAISS similarity search → top-k chunks
  3. Reranking: LLM-based contextual compression (Gemini)
  4. Generation: Reranked chunks → Gemini LLM → summarized answer
"""

from pathlib import Path

from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


def ingest_medical_pdf(pdf_path: str, faiss_index_path: str) -> None:
    """
    Pipeline for Document Ingestion:
    1. Loads a medical PDF.
    2. Uses RecursiveCharacterTextSplitter for chunking.
    3. Converts chunks to vectors using Gemini Embedding Model.
    4. Stores the vectors in a FAISS CPU vector store.
    """
    settings = get_settings()
    logger.info("rag_ingestion_start", pdf_path=pdf_path)

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(faiss_index_path)
    logger.info("rag_ingestion_complete", chunks=len(chunks), index_path=faiss_index_path)


def ask_medical_question(query: str, faiss_index_path: str | None = None) -> str:
    """
    Pipeline for Retrieval and Summary:
    1. Converts query to vector using Gemini Embedding model.
    2. Performs similarity search in FAISS.
    3. Applies reranking to the retrieved chunks using an LLM-based reranker/extractor.
    4. Sends reranked chunks to Gemini LLM for summarization.

    Falls back to direct LLM call if no FAISS index is available.
    """
    settings = get_settings()

    # Resolve FAISS index path from config if not provided
    if faiss_index_path is None:
        faiss_index_path = settings.FAISS_INDEX_PATH

    index_path = Path(faiss_index_path)
    logger.info("rag_query_start", query=query[:80])

    # Check if FAISS index exists
    if not index_path.exists() or not (index_path / "index.faiss").exists():
        logger.warning("rag_no_faiss_index", path=str(index_path))
        # Fallback: use Gemini directly without retrieval
        return _direct_llm_answer(query, settings.GEMINI_LLM_MODEL)

    # 1. Load Embeddings and FAISS Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        str(faiss_index_path), embeddings, allow_dangerous_deserialization=True
    )

    # Base retriever fetches top 5 most similar chunks
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 2. Apply Reranking (Using Gemini — no external providers)
    llm_for_rerank = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)
    compressor = LLMChainExtractor.from_llm(llm_for_rerank)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )

    # 3. LLM for Summary Generation
    summary_llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_LLM_MODEL, temperature=0.2
    )

    prompt_template = ChatPromptTemplate.from_template(
        "You are a medical AI assistant. Summarize an answer to the user's question "
        "based ONLY on the provided retrieved medical context.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Summary Answer:"
    )

    def format_docs(docs) -> str:  # type: ignore[no-untyped-def]
        return "\n\n".join(doc.page_content for doc in docs)

    # Build the RAG pipeline chain
    rag_chain = (
        {"context": compression_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | summary_llm
        | StrOutputParser()
    )

    logger.info("rag_retrieval_start")
    response: str = str(rag_chain.invoke(query))
    logger.info("rag_query_complete")
    return response


def _direct_llm_answer(query: str, model_name: str) -> str:
    """Fallback: answer a medical question directly via Gemini without retrieval."""
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
    prompt = ChatPromptTemplate.from_template(
        "You are a medical AI assistant. Answer the following medical question "
        "clearly and concisely. If you are not confident, advise the user to "
        "consult a healthcare professional.\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    chain = prompt | llm | StrOutputParser()
    result: str = str(chain.invoke({"question": query}))
    return result


if __name__ == "__main__":
    # Example usage:
    # set GOOGLE_API_KEY=your_api_key_here

    pdf_file = "sample_medical_document.pdf"
    index_dir = "ml/models/faiss_index"

    # Un-comment to test ingestion (requires a real PDF file)
    # ingest_medical_pdf(pdf_file, index_dir)

    # Un-comment to test querying
    # answer = ask_medical_question("What are the side effects of this treatment?", index_dir)
    # print("\nFinal Answer:\n", answer)
