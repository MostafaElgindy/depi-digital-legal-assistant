"""
Documents Router Module
========================
API routes for document management.
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import uuid
import shutil

from services.rag_service import get_rag_service, RAGService
from services.document_processor import get_document_processor_service, DocumentProcessorService
from services.vector_store import get_vector_store_service, VectorStoreService
from schemas.response import DocumentUploadResponse
from utils.toon_utils import TOONResponse, parse_toon_request
from core.config import get_settings

# Create Router
router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
    responses={
        500: {"description": "Internal Server Error"}
    }
)

# Document storage folder
UPLOAD_DIR = "data/uploads"


@router.post(
    "/upload",
    response_class=TOONResponse,
    summary="Upload PDF document"
)
async def upload_document(
    file: UploadFile = File(..., description="PDF file"),
    document_name: Optional[str] = Form(None, description="Document name"),
    rag_service: RAGService = Depends(get_rag_service),
    doc_processor: DocumentProcessorService = Depends(get_document_processor_service),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Upload and process a new PDF file.
    
    - File is saved in data/uploads folder
    - Document is split and added to Vector Store
    """
    try:
        # Verify file type
        if not file.filename.endswith('.pdf'):
            return TOONResponse(
                content={
                    "success": False,
                    "error_code": "INVALID_FILE_TYPE",
                    "error_message": "File must be in PDF format"
                },
                status_code=400
            )
        
        # Create storage folder
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Generate unique name
        doc_id = str(uuid.uuid4())
        file_name = f"{doc_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        chunks = doc_processor.process_pdf(file_path)
        
        # Add to Vector Store
        vector_store.add_documents(chunks)
        
        # Prepare response
        response = DocumentUploadResponse(
            success=True,
            document_id=doc_id,
            document_name=document_name or file.filename,
            chunks_created=len(chunks),
            message="Document uploaded and processed successfully"
        )
        
        return TOONResponse(
            content=response.model_dump(),
            status_code=201
        )
    
    except Exception as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "UPLOAD_ERROR",
                "error_message": f"File upload error: {str(e)}"
            },
            status_code=500
        )


@router.post(
    "/initialize",
    response_class=TOONResponse,
    summary="Initialize default documents"
)
async def initialize_documents(
    request: Request,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Initialize system with default documents.
    
    Custom PDF path can be specified in request:
    ```toon
    pdf_path = "data/my_document.pdf"
    ```
    """
    try:
        # Read request (optional)
        toon_data = await parse_toon_request(request)
        pdf_path = toon_data.get('pdf_path')
        
        # Initialize service
        rag_service.initialize(pdf_path)
        
        status = rag_service.get_status()
        
        return TOONResponse(
            content={
                "success": True,
                "message": "System initialized successfully",
                "status": status
            },
            status_code=200
        )
    
    except FileNotFoundError as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "FILE_NOT_FOUND",
                "error_message": str(e)
            },
            status_code=404
        )
    
    except Exception as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "INITIALIZATION_ERROR",
                "error_message": f"Initialization error: {str(e)}"
            },
            status_code=500
        )


@router.get(
    "/list",
    response_class=TOONResponse,
    summary="List documents"
)
async def list_documents(
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """
    Get list of loaded documents.
    """
    try:
        # Get file list
        uploaded_files = []
        if os.path.exists(UPLOAD_DIR):
            uploaded_files = os.listdir(UPLOAD_DIR)
        
        return TOONResponse(
            content={
                "success": True,
                "total_chunks": vector_store.document_count,
                "is_initialized": vector_store.is_initialized,
                "uploaded_files": uploaded_files
            },
            status_code=200
        )
    
    except Exception as e:
        return TOONResponse(
            content={
                "success": False,
                "error_code": "LIST_ERROR",
                "error_message": str(e)
            },
            status_code=500
        )
