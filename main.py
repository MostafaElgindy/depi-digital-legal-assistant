"""
Al-Dustour AI - Egyptian Constitution Expert
=============================================
FastAPI application for answering legal questions
using the Egyptian Constitution and RAG system.

Author: Arabic RAG Team
Version: 1.0.0
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys

# Add root path to project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import get_settings
from routers import query, documents, health
from utils.toon_utils import TOONResponse, TOON_CONTENT_TYPE
from services.rag_service import get_rag_service


# ==================== Lifespan ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Executes code on startup and shutdown.
    """
    # Startup
    settings = get_settings()
    print("=" * 50)
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print("=" * 50)
    
    # Initialize RAG Service (optional - can be initialized later)
    rag_service = get_rag_service()
    
    # Try to initialize default documents if they exist
    if os.path.exists(settings.pdf_path):
        print(f"📄 Found default PDF: {settings.pdf_path}")
        try:
            rag_service.initialize()
        except Exception as e:
            print(f"⚠️ Could not auto-initialize: {e}")
            print("⚠️ Please initialize manually via /api/documents/initialize")
    else:
        print(f"⚠️ Default PDF not found: {settings.pdf_path}")
        print("⚠️ Please upload a document or initialize manually")
    
    print("=" * 50)
    print(f"✅ Server running at http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# ==================== Create App ====================

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="""
    ## 🇪🇬 Al-Dustour AI - Egyptian Constitution Advisor
    
    AI application for answering legal questions
    related to the Egyptian Constitution.
    
    ### Features:
    - 🔍 **Semantic Search**: Using Embeddings for document search
    - 🤖 **LLM**: Using Groq Llama-3.3-70B for answers
    - 📄 **RAG**: Retrieval-Augmented Generation
    - 🔄 **TOON**: Alternative data format to JSON
    
    ### Data Format:
    This application uses **TOON** format for serialization instead of JSON.
    
    Request example:
    ```
    query = "Can civilians be tried before military courts?"
    num_results = 5
    include_sources = true
    ```
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==================== Middleware ====================

# CORS - In production, specify allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Include Routers ====================

app.include_router(query.router)
app.include_router(documents.router)
app.include_router(health.router)


# ==================== Static Files ====================

# Create static directories if they don't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ==================== Root Routes ====================

@app.get("/", include_in_schema=False)
async def root():
    """
    Home page - Serve the user interface.
    """
    index_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # If interface doesn't exist, return welcome message
    return TOONResponse(
        content={
            "success": True,
            "message": "Welcome to Al-Dustour AI",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "endpoints": {
                "docs": "/docs",
                "health": "/api/health",
                "query": "/api/query/ask",
                "documents": "/api/documents"
            }
        },
        status_code=200
    )


@app.get("/api", response_class=TOONResponse)
async def api_info():
    """
    API information endpoint.
    """
    return TOONResponse(
        content={
            "success": True,
            "app_name": settings.app_name,
            "version": settings.app_version,
            "data_format": "TOON",
            "content_type": TOON_CONTENT_TYPE,
            "endpoints": {
                "query": {
                    "ask": "POST /api/query/ask",
                    "status": "GET /api/query/status"
                },
                "documents": {
                    "upload": "POST /api/documents/upload",
                    "initialize": "POST /api/documents/initialize",
                    "list": "GET /api/documents/list"
                },
                "health": {
                    "check": "GET /api/health",
                    "ping": "GET /api/health/ping",
                    "detailed": "GET /api/health/detailed"
                }
            }
        },
        status_code=200
    )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP exception handler.
    """
    return TOONResponse(
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "error_message": exc.detail
        },
        status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler.
    """
    return TOONResponse(
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "error_message": str(exc) if settings.debug else "Internal server error"
        },
        status_code=500
    )


# ==================== Run ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
