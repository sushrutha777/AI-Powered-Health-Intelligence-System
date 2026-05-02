"""
RAG pipeline — orchestrates retrieval, prompt construction, and generation.

Implements the full Retrieval-Augmented Generation flow:
query → FAISS retrieval → context assembly → LLM generation → response.
"""
from typing import Any

from src.core.logging import get_logger
from src.schemas.chat import SourceCitation
from src.services.rag.llm_client import get_llm_client
from src.services.rag.vector_store import search

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a knowledgeable medical AI assistant for the Health Intelligence System.
Your role is to provide accurate, helpful medical information based on the provided context.

IMPORTANT GUIDELINES:
1. Always base your answers on the provided medical context when available.
2. If the context doesn't contain relevant information, say so clearly.
3. Always recommend consulting a healthcare professional for medical decisions.
4. Never provide definitive diagnoses — offer information and guidance only.
5. Be empathetic, clear, and use accessible language.
6. Cite which sources you used when possible."""

CONTEXT_TEMPLATE = """
--- MEDICAL CONTEXT ---
{context}
--- END CONTEXT ---

User Question: {question}

Please provide a thorough, accurate answer based on the medical context above.
If the context is insufficient, acknowledge this and provide general guidance.
Always recommend consulting a healthcare professional."""


def _build_prompt(question: str, context_docs: list[dict[str, Any]]) -> str:
    """Construct the full prompt with system instructions and retrieved context."""
    if context_docs:
        context_text = "\n\n".join(
            f"[Source: {doc.get('title', 'Unknown')}]\n{doc['content'][:500]}"
            for doc in context_docs
        )
    else:
        context_text = "No specific medical context available for this query."

    user_prompt = CONTEXT_TEMPLATE.format(context=context_text, question=question)
    return f"{SYSTEM_PROMPT}\n\n{user_prompt}"


async def generate_response(
    question: str, top_k: int = 5,
) -> tuple[str, list[SourceCitation]]:
    """
    Full RAG pipeline: retrieve → prompt → generate.

    Returns:
        Tuple of (response_text, source_citations).
    """
    # 1. Retrieve relevant documents
    context_docs = search(question, top_k=top_k)

    # 2. Build citations
    citations = [
        SourceCitation(
            title=doc.get("title", "Unknown"),
            content_snippet=doc["content"][:200],
            relevance_score=doc.get("score", 0.0),
        )
        for doc in context_docs
    ]

    # 3. Build prompt and generate
    prompt = _build_prompt(question, context_docs)
    llm_client = get_llm_client()
    response_text = await llm_client.generate(prompt)

    logger.info("rag_response_generated", question_length=len(question),
                num_sources=len(citations), response_length=len(response_text))

    return response_text, citations
