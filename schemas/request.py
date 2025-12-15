"""
Request Schemas
================
Data schemas for incoming requests.
Using Pydantic for data validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """
    Query request schema.
    Used when sending a question to the system.
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Legal question in Arabic",
        examples=["Can civilians be tried before military courts?"]
    )
    num_results: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of retrieved results"
    )
    include_sources: Optional[bool] = Field(
        default=True,
        description="Include sources in response"
    )
    
    class Config:
        """Schema configuration"""
        str_strip_whitespace = True


class DocumentUploadRequest(BaseModel):
    """
    Document upload request schema.
    """
    document_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Document name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Document description"
    )
    
    class Config:
        """Schema configuration"""
        str_strip_whitespace = True


class HealthCheckRequest(BaseModel):
    """
    Health check request schema.
    """
    include_details: Optional[bool] = Field(
        default=False,
        description="Include additional details"
    )
