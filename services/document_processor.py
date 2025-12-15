"""
Document Processor Service Module
==================================
Document (PDF) processing and splitting service.
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from typing import List, Optional
import os
import uuid

from core.config import get_settings
from models.document import Document, DocumentChunk


class DocumentProcessorService:
    """
    Document processing service.
    Loads PDF files and splits them into chunks.
    """
    
    def __init__(self):
        """Initialize document processing service"""
        self._settings = get_settings()
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            separators=["\n\n", "\n", ".", " "],
            length_function=len
        )
    
    def load_pdf(self, pdf_path: str) -> List[LangchainDocument]:
        """
        Load PDF file.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List[LangchainDocument]: List of document pages
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"⏳ Loading PDF: {pdf_path}...")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        print(f"📄 Loaded {len(documents)} pages from PDF")
        
        return documents
    
    def split_documents(
        self,
        documents: List[LangchainDocument]
    ) -> List[LangchainDocument]:
        """
        Split documents into smaller chunks.
        
        Args:
            documents: List of documents
        
        Returns:
            List[LangchainDocument]: List of chunks
        """
        print(f"⏳ Splitting {len(documents)} documents into chunks...")
        
        splits = self._text_splitter.split_documents(documents)
        
        # Add extra info to metadata
        for i, split in enumerate(splits):
            split.metadata['chunk_index'] = i
        
        print(f"📄 Created {len(splits)} chunks")
        
        return splits
    
    def process_pdf(
        self,
        pdf_path: Optional[str] = None
    ) -> List[LangchainDocument]:
        """
        Complete PDF processing (load + split).
        
        Args:
            pdf_path: File path (optional, uses default)
        
        Returns:
            List[LangchainDocument]: List of chunks
        """
        path = pdf_path or self._settings.pdf_path
        
        # Load
        documents = self.load_pdf(path)
        
        # Split
        splits = self.split_documents(documents)
        
        return splits
    
    def create_document_model(
        self,
        pdf_path: str,
        chunks: List[LangchainDocument]
    ) -> Document:
        """
        Create Document model from chunks.
        
        Args:
            pdf_path: File path
            chunks: List of chunks
        
        Returns:
            Document: Document model
        """
        doc_chunks = []
        
        for chunk in chunks:
            doc_chunk = DocumentChunk(
                content=chunk.page_content,
                page_number=chunk.metadata.get('page', 0),
                chunk_index=chunk.metadata.get('chunk_index', 0),
                metadata=chunk.metadata
            )
            doc_chunks.append(doc_chunk)
        
        return Document(
            id=str(uuid.uuid4()),
            name=os.path.basename(pdf_path),
            file_path=pdf_path,
            chunks=doc_chunks,
            total_pages=max(c.page_number for c in doc_chunks) + 1 if doc_chunks else 0
        )


# ==================== Dependency Injection ====================

_document_processor_instance: Optional[DocumentProcessorService] = None


def get_document_processor_service() -> DocumentProcessorService:
    """
    Get document processor service instance.
    
    Returns:
        DocumentProcessorService: Service instance
    """
    global _document_processor_instance
    
    if _document_processor_instance is None:
        _document_processor_instance = DocumentProcessorService()
    
    return _document_processor_instance


def reset_document_processor_service() -> None:
    """Reset document processor service"""
    global _document_processor_instance
    _document_processor_instance = None
