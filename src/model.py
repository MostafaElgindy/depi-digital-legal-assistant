import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from llama_index.core import StorageContext, VectorStoreIndex, PromptTemplate, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms import ChatMessage, MessageRole
from dotenv import load_dotenv

load_dotenv()

# Load environment variables from a specific .env file
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
if os.path.exists(config_path):
    load_dotenv(config_path)

# Initialize constants
pdf_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'constitution.pdf')
google_api_key = os.getenv("GOOGLE_API_KEY", "")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
os.environ["GOOGLE_API_KEY"] = google_api_key

collection_name = os.path.splitext(os.path.basename(pdf_file_path))[0]

# Function to set up the database and collection
def setup_chroma_collection():
    """Initialize ChromaDB client and create a collection."""
    huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Initialize ChromaDB client and create a collection
    db = chromadb.Client()
    return db.get_or_create_collection(name=collection_name, embedding_function=huggingface_ef)

# Function to create the vector store and index
def create_vector_store_and_index(chroma_collection):
    """Create vector store and storage context."""
    # Create an embedding model (Free & Local)
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    Settings.embed_model = embed_model

    # Initialize vector store and storage context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create the index from the existing vector store
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, embed_model=embed_model)

    return index

# Function to set up the chat engine
def setup_chat_engine(index):
    """Initialize the chat engine."""
    llm = Gemini(model="models/gemini-2.5-flash", temperature=0)
    Settings.llm = llm
    
    query_engine = index.as_query_engine(llm=llm)
    
    chat_history = []

    # Set up the chat engine
    chat_engine = SimpleChatEngine.from_defaults(
        query_engine=query_engine,
        llm=llm
    )

    return chat_engine, chat_history

# Function to handle chat queries
def chat_with_memory(chat_engine, chat_history, user_query):
    """Process the user's query and update chat history."""
    chat_history.append(ChatMessage(role=MessageRole.USER, content=user_query))
    response = chat_engine.chat(user_query)
    chat_history.append(ChatMessage(
        role=MessageRole.ASSISTANT, content=str(response)))
    return response