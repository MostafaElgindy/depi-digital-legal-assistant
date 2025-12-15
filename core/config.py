"""
Core Configuration Module
=========================
Central application settings using Pydantic Settings.
All variables are read from Environment Variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Main application settings.
    All values are read from Environment Variables.
    """
    
    # ==================== App Settings ====================
    app_name: str = Field(
        default="Al-Dustour AI",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    # ==================== Groq LLM Settings ====================
    groq_api_key: str = Field(
        ...,
        description="Groq API key",
        env="GROQ_API_KEY"
    )
    llm_model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="LLM model name"
    )
    llm_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Response randomness degree"
    )
    llm_max_tokens: int = Field(
        default=1024,
        ge=1,
        le=8192,
        description="Maximum generated tokens"
    )
    
    # ==================== Embeddings Settings ====================
    embedding_model_name: str = Field(
        default="intfloat/multilingual-e5-large",
        description="Text embedding model for Arabic"
    )
    embedding_device: str = Field(
        default="cpu",
        description="Device used for embedding (cpu/cuda)"
    )
    
    # ==================== Vector Store Settings ====================
    vector_store_path: Optional[str] = Field(
        default=None,
        description="Path to save Vector database"
    )
    retrieval_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of retrieved documents"
    )
    
    # ==================== Document Processing Settings ====================
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Size of each text chunk"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=500,
        description="Overlap between chunks"
    )
    pdf_path: str = Field(
        default="data/Egyptian_Constitution.pdf",
        description="Path to Constitution PDF file"
    )
    
    # ==================== Server Settings ====================
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (Cached).
    Uses lru_cache to ensure only one instance is created.
    
    Returns:
        Settings: Settings object
    """
    return Settings()


# ==================== Prompt Templates ====================

SYSTEM_PROMPT_TEMPLATE = """أنت مستشار قانوني خبير في الدستور المصري.
مهمتك هي الإجابة على سؤال المستخدم بناءً *فقط* على النصوص الدستورية المقدمة أدناه.

التعليمات:
1. اقرأ النصوص المقدمة بعناية.
2. لا تستخدم معلومات خارجية إذا لم تكن موجودة في النصوص.
3. اشرح إجابتك بوضوح واستشهد برقم المادة إن وجد.
4. إذا كانت الإجابة غير موجودة في النصوص، قل "لا توجد معلومات كافية في الوثائق المتاحة".
5. أجب باللغة العربية دائمًا.
"""

USER_PROMPT_TEMPLATE = """
النصوص الدستورية المتاحة (Context):
{context}

سؤال المستخدم:
{query}
"""
