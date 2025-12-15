"""
Embeddings Service Module
==========================
Text Embeddings service for Arabic texts.
Uses multilingual-e5-large model.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Optional
import numpy as np

from core.config import get_settings


class EmbeddingsService:
    """
    Text embeddings service.
    Converts texts to vectors for semantic search.
    """
    
    def __init__(self):
        """
        Initialize embeddings service.
        Model is loaded on creation.
        """
        self._settings = get_settings()
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """
        Load embeddings model.
        Called on application startup.
        """
        if self._is_initialized:
            return
        
        print(f"⏳ Loading Embeddings Model: {self._settings.embedding_model_name}...")
        
        self._embeddings = HuggingFaceEmbeddings(
            model_name=self._settings.embedding_model_name,
            model_kwargs={'device': self._settings.embedding_device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self._is_initialized = True
        print("✅ Embeddings Model Loaded Successfully!")
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._is_initialized
    
    @property
    def model(self) -> HuggingFaceEmbeddings:
        """Get embeddings object"""
        if not self._is_initialized:
            self.initialize()
        return self._embeddings
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to vector.
        
        Args:
            text: Text to convert
        
        Returns:
            List[float]: Embedding vector
        """
        if not self._is_initialized:
            self.initialize()
        
        return self._embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convert list of texts to vectors.
        
        Args:
            texts: List of texts
        
        Returns:
            List[List[float]]: List of vectors
        """
        if not self._is_initialized:
            self.initialize()
        
        return self._embeddings.embed_documents(texts)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            float: Similarity score (0-1)
        """
        vec1 = np.array(self.embed_text(text1))
        vec2 = np.array(self.embed_text(text2))
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
    def health_check(self) -> bool:
        """
        Check embeddings service health.
        
        Returns:
            bool: True if service is working
        """
        try:
            test_embedding = self.embed_text("test")
            return len(test_embedding) > 0
        except Exception:
            return False


# ==================== Dependency Injection ====================

_embeddings_service_instance: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """
    Get embeddings service instance (Singleton).
    
    Returns:
        EmbeddingsService: Embeddings service instance
    """
    global _embeddings_service_instance
    
    if _embeddings_service_instance is None:
        _embeddings_service_instance = EmbeddingsService()
    
    return _embeddings_service_instance


def reset_embeddings_service() -> None:
    """Reset embeddings service"""
    global _embeddings_service_instance
    _embeddings_service_instance = None
