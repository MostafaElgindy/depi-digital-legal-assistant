"""
Vector Store Service Module
============================
Vector database service using FAISS.
Used for semantic document search.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangchainDocument
from typing import List, Optional, Tuple
import os

from core.config import get_settings
from services.embeddings import get_embeddings_service, EmbeddingsService
from models.document import DocumentChunk, RetrievedContext


class VectorStoreService:
    """
    Vector Store service for semantic search.
    Uses FAISS for document storage and retrieval.
    """
    
    def __init__(self, embeddings_service: Optional[EmbeddingsService] = None):
        """
        Initialize Vector Store service.
        
        Args:
            embeddings_service: Embeddings service (optional)
        """
        self._settings = get_settings()
        self._embeddings_service = embeddings_service or get_embeddings_service()
        self._vector_store: Optional[FAISS] = None
        self._is_initialized = False
        self._document_count = 0
    
    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized"""
        return self._is_initialized
    
    @property
    def document_count(self) -> int:
        """Number of stored documents"""
        return self._document_count
    
    def initialize_from_documents(
        self,
        documents: List[LangchainDocument]
    ) -> None:
        """
        Initialize Vector Store from document list.
        
        Args:
            documents: List of LangChain documents
        """
        if not self._embeddings_service.is_initialized:
            self._embeddings_service.initialize()
        
        print(f"⏳ Creating Vector Store with {len(documents)} documents...")
        
        self._vector_store = FAISS.from_documents(
            documents,
            self._embeddings_service.model
        )
        
        self._document_count = len(documents)
        self._is_initialized = True
        
        print("✅ Vector Store Created Successfully!")
    
    def add_documents(self, documents: List[LangchainDocument]) -> None:
        """
        Add new documents to the database.
        
        Args:
            documents: List of new documents
        """
        if not self._is_initialized:
            self.initialize_from_documents(documents)
            return
        
        self._vector_store.add_documents(documents)
        self._document_count += len(documents)
    
    def search(
        self,
        query: str,
        k: Optional[int] = None
    ) -> RetrievedContext:
        """
        Search for documents similar to query.
        
        Args:
            query: Query text
            k: Number of results (optional)
        
        Returns:
            RetrievedContext: Retrieved context
        """
        if not self._is_initialized:
            raise RuntimeError("Vector Store is not initialized. Call initialize_from_documents first.")
        
        k = k or self._settings.retrieval_k
        
        # Search with relevance scores
        results_with_scores = self._vector_store.similarity_search_with_score(
            query,
            k=k
        )
        
        chunks = []
        scores = []
        
        for doc, score in results_with_scores:
            chunk = DocumentChunk(
                content=doc.page_content,
                page_number=doc.metadata.get('page', 0),
                chunk_index=doc.metadata.get('chunk_index', 0),
                metadata=doc.metadata
            )
            chunks.append(chunk)
            scores.append(float(score))
        
        return RetrievedContext(
            chunks=chunks,
            query=query,
            relevance_scores=scores
        )
    
    def search_simple(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[LangchainDocument]:
        """
        Simple search returning LangChain documents.
        
        Args:
            query: Query text
            k: Number of results
        
        Returns:
            List[LangchainDocument]: List of documents
        """
        if not self._is_initialized:
            raise RuntimeError("Vector Store is not initialized.")
        
        k = k or self._settings.retrieval_k
        
        return self._vector_store.similarity_search(query, k=k)
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save Vector Store to disk.
        
        Args:
            path: Save path (optional)
        """
        if not self._is_initialized:
            raise RuntimeError("Vector Store is not initialized.")
        
        save_path = path or self._settings.vector_store_path
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self._vector_store.save_local(save_path)
            print(f"✅ Vector Store saved to: {save_path}")
    
    def load(self, path: Optional[str] = None) -> None:
        """
        Load Vector Store from disk.
        
        Args:
            path: Load path (optional)
        """
        if not self._embeddings_service.is_initialized:
            self._embeddings_service.initialize()
        
        load_path = path or self._settings.vector_store_path
        
        if load_path and os.path.exists(load_path):
            self._vector_store = FAISS.load_local(
                load_path,
                self._embeddings_service.model,
                allow_dangerous_deserialization=True
            )
            self._is_initialized = True
            print(f"✅ Vector Store loaded from: {load_path}")
    
    def health_check(self) -> bool:
        """
        Check Vector Store health.
        
        Returns:
            bool: True if database is working
        """
        try:
            if not self._is_initialized:
                return False
            
            # Simple search test
            results = self.search_simple("test", k=1)
            return True
        except Exception:
            return False


# ==================== Dependency Injection ====================

_vector_store_instance: Optional[VectorStoreService] = None


def get_vector_store_service() -> VectorStoreService:
    """
    Get Vector Store service instance (Singleton).
    
    Returns:
        VectorStoreService: Service instance
    """
    global _vector_store_instance
    
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    
    return _vector_store_instance


def reset_vector_store_service() -> None:
    """Reset Vector Store service"""
    global _vector_store_instance
    _vector_store_instance = None
