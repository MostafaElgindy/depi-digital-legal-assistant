"""
Query Router Module
====================
API routes for queries and questions.
Uses TOON for serialization and deserialization.
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Optional

from services.rag_service import get_rag_service, RAGService
from schemas.request import QueryRequest
from schemas.response import QueryResponse, ErrorResponse
from utils.toon_utils import (
    TOONResponse,
    parse_toon_request,
    toon_to_pydantic,
    create_error_toon
)

# Create Router
router = APIRouter(
    prefix="/api/query",
    tags=["Query"],
    responses={
        500: {"description": "Internal Server Error"}
    }
)


@router.post(
    "/ask",
    response_class=TOONResponse,
    summary="Ask a legal question",
    description="""
    Receive a legal question in Arabic and answer it
    using the RAG system and Egyptian Constitution.
    
    **Request format:** TOON
    **Response format:** TOON
    """
)
async def ask_question(
    request: Request,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ask a question and get an answer from the Egyptian Constitution.
    
    Receives request in TOON format and responds in same format.
    
    Request example:
    ```toon
    query = "Can civilians be tried before military courts?"
    num_results = 5
    include_sources = true
    ```
    """
    try:
        # Read and parse TOON request
        toon_data = await parse_toon_request(request)
        
        # Convert to Pydantic
        query_request = QueryRequest(**toon_data)
        
        # Check service initialization
        if not rag_service.is_initialized:
            return TOONResponse(
                content={
                    "success": False,
                    "error_code": "SERVICE_NOT_INITIALIZED",
                    "error_message": "RAG service not initialized. Please upload documents first."
                },
                status_code=503
            )
        
        # Process question
        response = await rag_service.ask(
            query=query_request.query,
            num_results=query_request.num_results,
            include_sources=query_request.include_sources
        )
        
        # Return response in TOON format
        return TOONResponse(
            content=response.model_dump(),
            status_code=200
        )
    
    except ValueError as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "INVALID_REQUEST",
                "error_message": f"Invalid request: {str(e)}"
            },
            status_code=400
        )
    
    except Exception as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "error_message": f"Internal error: {str(e)}"
            },
            status_code=500
        )


@router.get(
    "/status",
    response_class=TOONResponse,
    summary="Query service status"
)
async def get_query_status(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Get query service status.
    """
    status = rag_service.get_status()
    
    return TOONResponse(
        content={
            "success": True,
            "status": status
        },
        status_code=200
    )
