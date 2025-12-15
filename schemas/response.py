"""
Response Schemas
=================
Data schemas for outgoing responses.
Using Pydantic for organization and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SourceChunk(BaseModel):
    """
    Source chunk schema.
    """
    content: str = Field(..., description="Chunk content")
    page_number: int = Field(..., description="Page number")
    chunk_index: int = Field(..., description="Chunk order")
    relevance_score: Optional[float] = Field(
        default=None, 
        description="Relevance score"
    )


class QueryResponse(BaseModel):
    """
    Query response schema.
    Returned when answering user question.
    """
    success: bool = Field(..., description="Operation success status")
    query: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: Optional[List[SourceChunk]] = Field(
        default=None,
        description="Sources used"
    )
    model_used: str = Field(..., description="Model used")
    processing_time: Optional[float] = Field(
        default=None,
        description="Processing time in seconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )
    
    class Config:
        """Schema configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """
    Error response schema.
    Returned when processing error occurs.
    """
    success: bool = Field(default=False, description="Failure status")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[str] = Field(
        default=None,
        description="Additional details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )


class HealthCheckResponse(BaseModel):
    """
    Health check response schema.
    """
    status: str = Field(..., description="System status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    llm_status: str = Field(..., description="LLM model status")
    vector_store_status: str = Field(..., description="Database status")
    documents_loaded: int = Field(..., description="Number of loaded documents")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Check timestamp"
    )


class DocumentUploadResponse(BaseModel):
    """
    Document upload response schema.
    """
    success: bool = Field(..., description="Upload success status")
    document_id: str = Field(..., description="Document ID")
    document_name: str = Field(..., description="Document name")
    chunks_created: int = Field(..., description="Number of created chunks")
    message: str = Field(..., description="Descriptive message")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Upload timestamp"
    )
