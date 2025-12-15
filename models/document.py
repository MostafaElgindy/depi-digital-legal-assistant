"""
Document Models
================
Data models for documents.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class DocumentChunk:
    """
    Represents a document chunk after splitting.
    """
    content: str
    page_number: int
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }


@dataclass
class Document:
    """
    Represents a complete document.
    """
    id: str
    name: str
    file_path: str
    chunks: List[DocumentChunk] = field(default_factory=list)
    total_pages: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "total_pages": self.total_pages,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class RetrievedContext:
    """
    Represents context retrieved from Vector Store.
    """
    chunks: List[DocumentChunk]
    query: str
    relevance_scores: List[float] = field(default_factory=list)
    
    @property
    def combined_text(self) -> str:
        """Combine all chunks into single text"""
        return "\n\n".join([
            f"[Article/Chunk {i+1}]: {chunk.content}" 
            for i, chunk in enumerate(self.chunks)
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "query": self.query,
            "relevance_scores": self.relevance_scores,
            "combined_text": self.combined_text
        }


@dataclass
class LLMResponse:
    """
    Represents LLM model response.
    """
    answer: str
    model_name: str
    tokens_used: Optional[int] = None
    generation_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "answer": self.answer,
            "model_name": self.model_name,
            "tokens_used": self.tokens_used,
            "generation_time": self.generation_time
        }
