"""
Health Router Module
=====================
System health check routes.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from services.rag_service import get_rag_service, RAGService
from services.llm import get_llm_service, LLMService
from services.embeddings import get_embeddings_service, EmbeddingsService
from services.vector_store import get_vector_store_service, VectorStoreService
from schemas.response import HealthCheckResponse
from utils.toon_utils import TOONResponse
from core.config import get_settings

# Create Router
router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)


@router.get(
    "",
    response_class=TOONResponse,
    summary="System health check"
)
async def health_check(
    rag_service: RAGService = Depends(get_rag_service),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Check health of all system components.
    """
    settings = get_settings()
    
    # Check components
    health_status = rag_service.health_check()
    
    response = HealthCheckResponse(
        status="healthy" if all(health_status.values()) else "degraded",
        app_name=settings.app_name,
        version=settings.app_version,
        llm_status="online" if health_status.get("llm", False) else "offline",
        vector_store_status="online" if health_status.get("vector_store", False) else "offline",
        documents_loaded=vector_store.document_count,
        timestamp=datetime.now()
    )
    
    return TOONResponse(
        content=response.model_dump(),
        status_code=200
    )


@router.get(
    "/ping",
    response_class=TOONResponse,
    summary="Quick ping test"
)
async def ping():
    """
    Quick test to verify server is working.
    """
    return TOONResponse(
        content={
            "success": True,
            "message": "pong",
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )


@router.get(
    "/detailed",
    response_class=TOONResponse,
    summary="Detailed health check"
)
async def detailed_health_check(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Detailed health check of all services.
    """
    settings = get_settings()
    status = rag_service.get_status()
    health = rag_service.health_check()
    
    return TOONResponse(
        content={
            "success": True,
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "debug": settings.debug
            },
            "services": {
                "llm": {
                    "model": settings.llm_model_name,
                    "status": "online" if health.get("llm") else "offline"
                },
                "embeddings": {
                    "model": settings.embedding_model_name,
                    "status": "online" if health.get("embeddings") else "offline"
                },
                "vector_store": {
                    "status": "online" if health.get("vector_store") else "offline",
                    "document_count": status.get("document_count", 0)
                }
            },
            "config": {
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "retrieval_k": settings.retrieval_k,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens
            },
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )
