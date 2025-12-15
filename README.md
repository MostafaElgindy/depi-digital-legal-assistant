# Al-Dustour AI - Egyptian Constitution Expert 🇪🇬

A professional AI application for answering legal questions related to the Egyptian Constitution.

## 🌟 Features

- **RAG (Retrieval-Augmented Generation)**: Combines retrieval with generation for accurate answers
- **Groq LLM**: Uses Llama-3.3-70B-Versatile model via Groq API
- **TOON Serialization**: Alternative format to JSON for serialization
- **Arabic User Interface**: Professional RTL design, easy to use
- **Extensible**: Clean Architecture with SOLID principles

## 📁 Project Structure

```
arabic-rag-app/
├── main.py                      # FastAPI entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variables example
├── core/
│   ├── __init__.py
│   └── config.py                # Application settings
├── models/
│   ├── __init__.py
│   └── document.py              # Data models
├── schemas/
│   ├── __init__.py
│   ├── request.py               # Request schemas
│   └── response.py              # Response schemas
├── services/
│   ├── __init__.py
│   ├── llm.py                   # Groq LLM service ⭐
│   ├── embeddings.py            # Embeddings service
│   ├── vector_store.py          # FAISS service
│   ├── document_processor.py    # PDF processing
│   └── rag_service.py           # Main RAG service
├── routers/
│   ├── __init__.py
│   ├── query.py                 # Query API
│   ├── documents.py             # Documents API
│   └── health.py                # Health API
├── utils/
│   ├── __init__.py
│   └── toon_utils.py            # TOON ⭐
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
└── data/
    └── (PDF files)
```

## 🚀 Getting Started

### 1. Create Virtual Environment

```bash
cd arabic-rag-app
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
# Copy example file
copy .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_groq_api_key_here
```

### 4. Add PDF File

Place the Egyptian Constitution PDF in the `data/` folder:

```
data/Egyptian_Constitution.pdf
```

### 5. Run the Server

```bash
python main.py

# Or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open the Application

- **Main Interface**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query/ask` | Ask a legal question |
| GET | `/api/query/status` | Query service status |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload a PDF document |
| POST | `/api/documents/initialize` | Initialize default documents |
| GET | `/api/documents/list` | List documents |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health check |
| GET | `/api/health/ping` | Quick ping test |
| GET | `/api/health/detailed` | Detailed health check |

## 🔄 TOON Format

The application uses **TOON** format instead of JSON:

### Request Example:

```toon
query = "Can civilians be tried before military courts?"
num_results = 5
include_sources = true
```

### Response Example:

```toon
success = true
query = "Can civilians be tried before military courts?"
answer = "According to Article 204 of the Egyptian Constitution..."
model_used = "llama-3.3-70b-versatile"
processing_time = 2.345

[[sources]]
content = "Article 204: Military judiciary is an independent judicial body..."
page_number = 45
chunk_index = 123
```

## 🔧 Data Flow

```
[User] 
    ↓ (TOON Request)
[Frontend JS] 
    ↓ (HTTP POST with TOON body)
[FastAPI Router] 
    ↓ (Parse TOON → Pydantic)
[RAG Service]
    ↓
[Vector Store] → [Retrieval] → [Context]
    ↓
[LLM Service (Groq Llama-3.3-70B)]
    ↓
[Response Schema] 
    ↓ (Serialize to TOON)
[Frontend] 
    ↓ (Parse TOON, Display)
[User] ✅
```

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `LLM_MODEL_NAME` | LLM model name | `llama-3.3-70b-versatile` |
| `LLM_TEMPERATURE` | Randomness degree | `0.3` |
| `LLM_MAX_TOKENS` | Maximum tokens | `1024` |
| `EMBEDDING_MODEL_NAME` | Embedding model | `intfloat/multilingual-e5-large` |
| `EMBEDDING_DEVICE` | Embedding device | `cpu` |
| `CHUNK_SIZE` | Chunk size | `800` |
| `CHUNK_OVERLAP` | Overlap | `200` |
| `RETRIEVAL_K` | Number of results | `5` |
| `PDF_PATH` | PDF path | `data/Egyptian_Constitution.pdf` |
