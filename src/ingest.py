import os
import sys
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb.utils import embedding_functions
from utils import clean_text_arabic
from dotenv import load_dotenv

load_dotenv()


def create_collection_from_pdf(pdf_file_path):
    # Load documents from the PDF
    reader = SimpleDirectoryReader(input_files=[pdf_file_path])
    documents = reader.load_data()

    # Clean the text in the documents
    for document in documents:
        document.text = clean_text_arabic(document.text)

    huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Initialize ChromaDB client and create a collection
    db = chromadb.Client()
    collection_name = os.path.splitext(os.path.basename(pdf_file_path))[
        0]  # Use the file name without extension
    
    # تمرير الدالة المجانية للـ Collection
    chroma_collection = db.get_or_create_collection(
        name=collection_name, embedding_function=huggingface_ef)

    # Create an embedding model
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # Initialize vector store and storage context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create a VectorStoreIndex from the documents
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model)

    print(
        f"Collection '{collection_name}' created successfully with {len(documents)} documents.")
