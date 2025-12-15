"""
RAG Service Module
===================
Main RAG service that combines all components.
Coordinates between Vector Store and LLM to answer questions.
"""

from typing import Optional, Dict, Any
import time
import os

from core.config import get_settings
from services.llm import get_llm_service, LLMService
from services.embeddings import get_embeddings_service, EmbeddingsService
from services.vector_store import get_vector_store_service, VectorStoreService
from services.document_processor import get_document_processor_service, DocumentProcessorService
from models.document import RetrievedContext, LLMResponse
from schemas.response import QueryResponse, SourceChunk


class RAGService:
    """
    Main RAG service.
    Combines retrieval and generation to answer questions.
    """
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        embeddings_service: Optional[EmbeddingsService] = None,
        vector_store_service: Optional[VectorStoreService] = None,
        document_processor_service: Optional[DocumentProcessorService] = None
    ):
        """
        Initialize RAG service.
        
        Args:
            llm_service: LLM service (optional)
            embeddings_service: Embeddings service (optional)
            vector_store_service: Vector Store service (optional)
            document_processor_service: Document processor service (optional)
        """
        self._settings = get_settings()
        self._llm_service = llm_service or get_llm_service()
        self._embeddings_service = embeddings_service or get_embeddings_service()
        self._vector_store_service = vector_store_service or get_vector_store_service()
        self._document_processor_service = document_processor_service or get_document_processor_service()
        self._is_initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._is_initialized
    
    def initialize(self, pdf_path: Optional[str] = None) -> None:
        """
        Initialize RAG service (load documents and create Vector Store).
        
        Args:
            pdf_path: Path to PDF file (optional)
        """
        if self._is_initialized:
            print("⚠️ RAG Service already initialized")
            return
        
        path = pdf_path or self._settings.pdf_path
        
        print("🚀 Initializing RAG Service...")
        
        # Process PDF
        if os.path.exists(path):
            chunks = self._document_processor_service.process_pdf(path)
            
            # Create Vector Store
            self._vector_store_service.initialize_from_documents(chunks)
            
            self._is_initialized = True
            print("✅ RAG Service Initialized Successfully!")
        else:
            print(f"⚠️ PDF file not found: {path}")
            print("⚠️ RAG Service initialized without documents. Upload a document first.")
            self._is_initialized = True
    
    async def ask(
        self,
        query: str,
        num_results: Optional[int] = None,
        include_sources: bool = True
    ) -> QueryResponse:
        """
        Ask a question and get an answer.
        
        Args:
            query: The question
            num_results: Number of retrieved results
            include_sources: Include sources
        
        Returns:
            QueryResponse: Answer with sources
        """
        start_time = time.time()
        
        # Check initialization
        if not self._vector_store_service.is_initialized:
            raise RuntimeError("Vector Store is not initialized. Initialize RAG service first.")
        
        # 1. Retrieve context
        k = num_results or self._settings.retrieval_k
        context = self._vector_store_service.search(query, k=k)
        
        # 2. Generate answer
        llm_response = await self._llm_service.generate_response(
            query=query,
            context=context.combined_text
        )
        
        processing_time = time.time() - start_time
        
        # 3. Build response
        sources = None
        if include_sources:
            sources = [
                SourceChunk(
                    content=chunk.content,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    relevance_score=score if i < len(context.relevance_scores) else None
                )
                for i, (chunk, score) in enumerate(
                    zip(context.chunks, context.relevance_scores + [None] * len(context.chunks))
                )
            ]
        
        return QueryResponse(
            success=True,
            query=query,
            answer=llm_response.answer,
            sources=sources,
            model_used=llm_response.model_name,
            processing_time=round(processing_time, 3)
        )
    
    def ask_sync(
        self,
        query: str,
        num_results: Optional[int] = None,
        include_sources: bool = True
    ) -> QueryResponse:
        """
        Ask a question synchronously.
        
        Args:
            query: The question
            num_results: Number of results
            include_sources: Include sources
        
        Returns:
            QueryResponse: Answer
        """
        start_time = time.time()
        
        if not self._vector_store_service.is_initialized:
            raise RuntimeError("Vector Store is not initialized.")
        
        # Retrieve
        k = num_results or self._settings.retrieval_k
        context = self._vector_store_service.search(query, k=k)
        
        # Generate
        llm_response = self._llm_service.generate_response_sync(
            query=query,
            context=context.combined_text
        )
        
        processing_time = time.time() - start_time
        
        sources = None
        if include_sources:
            sources = [
                SourceChunk(
                    content=chunk.content,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    relevance_score=context.relevance_scores[i] if i < len(context.relevance_scores) else None
                )
                for i, chunk in enumerate(context.chunks)
            ]
        
        return QueryResponse(
            success=True,
            query=query,
            answer=llm_response.answer,
            sources=sources,
            model_used=llm_response.model_name,
            processing_time=round(processing_time, 3)
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get service status.
        
        Returns:
            Dict: Status information
        """
        return {
            "is_initialized": self._is_initialized,
            "vector_store_initialized": self._vector_store_service.is_initialized,
            "embeddings_initialized": self._embeddings_service.is_initialized,
            "document_count": self._vector_store_service.document_count,
            "llm_model": self._llm_service.model_name
        }
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all components.
        
        Returns:
            Dict[str, bool]: Status of each component
        """
        return {
            "llm": self._llm_service.health_check(),
            "embeddings": self._embeddings_service.health_check() if self._embeddings_service.is_initialized else False,
            "vector_store": self._vector_store_service.health_check() if self._vector_store_service.is_initialized else False
        }


# ==================== Dependency Injection ====================

_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get RAG service instance (Singleton).
    
    Returns:
        RAGService: Service instance
    """
    global _rag_service_instance
    
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    
    return _rag_service_instance


def reset_rag_service() -> None:
    """Reset RAG service"""
    global _rag_service_instance
    _rag_service_instance = None
