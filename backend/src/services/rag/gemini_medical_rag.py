import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

def ingest_medical_pdf(pdf_path: str, faiss_index_path: str) -> None:
    """
    Pipeline for Document Ingestion:
    1. Loads a medical PDF.
    2. Uses RecursiveCharacterTextSplitter for chunking.
    3. Converts chunks to vectors using Gemini Embedding Model.
    4. Stores the vectors in a FAISS CPU vector store.
    """
    print(f"Loading PDF from {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    print("Generating embeddings using Gemini and saving to FAISS...")
    # Requires GOOGLE_API_KEY environment variable
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save the FAISS index locally
    vectorstore.save_local(faiss_index_path)
    print(f"Vector store successfully saved to {faiss_index_path}")

def ask_medical_question(query: str, faiss_index_path: str) -> str:
    """
    Pipeline for Retrieval and Summary:
    1. Converts query to vector using Gemini Embedding model.
    2. Performs similarity search in FAISS.
    3. Applies reranking to the retrieved chunks using an LLM-based reranker/extractor.
    4. Sends reranked chunks to Gemini LLM for summarization.
    """
    print(f"Processing query: '{query}'")
    
    # 1. Load Embeddings and FAISS Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    
    # Base retriever fetches top 10 most similar chunks
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 2. Apply Reranking (Using Gemini itself! No HuggingFace)
    print("Setting up Gemini-based Reranker (LLM Extractor)...")
    llm_for_rerank = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)
    
    # The LLMChainExtractor uses the LLM to process each retrieved document 
    # and "rerank" by extracting only the relevant information (or dropping irrelevant ones)
    compressor = LLMChainExtractor.from_llm(llm_for_rerank)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=base_retriever
    )

    # 3. LLM for Summary Generation
    print("Initializing Gemini LLM for summary...")
    summary_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    prompt_template = ChatPromptTemplate.from_template(
        "You are a medical AI assistant. Summarize an answer to the user's question based ONLY on the provided retrieved medical context.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Summary Answer:"
    )
    
    def format_docs(docs) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    # Build the RAG pipeline chain
    rag_chain = (
        {"context": compression_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | summary_llm
        | StrOutputParser()
    )

    print("Retrieving, reranking, and generating summary...")
    response = rag_chain.invoke(query)
    return response

if __name__ == "__main__":
    # Example usage:
    # Set your google api key in the terminal first:
    # set GOOGLE_API_KEY=your_api_key_here
    
    pdf_file = "sample_medical_document.pdf"
    index_dir = "faiss_medical_index"
    
    # Un-comment to test ingestion (requires a real PDF file)
    # ingest_medical_pdf(pdf_file, index_dir)
    
    # Un-comment to test querying
    # answer = ask_medical_question("What are the side effects of this treatment?", index_dir)
    # print("\nFinal Answer:\n", answer)
