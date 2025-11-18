# Constitution Study Chatbot - Senior Project

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Project Overview

**Constitution Study Chatbot** is an intelligent document retrieval and question-answering system designed specifically for studying the **Egyptian Constitution (2014)**. The application leverages advanced AI technologies to provide accurate, context-aware responses to user queries about constitutional articles and provisions.

This is a **Senior Project** developed by **AI Engineering students** combining modern web technologies with cutting-edge AI capabilities including semantic search, vector embeddings, and large language models.

### Key Features

- **PDF Document Upload**: Users can upload the Egyptian Constitution PDF for analysis
- **Intelligent Question Answering**: Ask questions in natural language and receive precise answers from the constitutional text
- **Vector Search**: Advanced semantic search using ChromaDB for accurate document retrieval
- **AI-Powered Responses**: Google Gemini integration for generating comprehensive answers
- **Real-time Chat Interface**: Modern, responsive web interface with smooth messaging
- **TOON Protocol**: Lightweight Token-Oriented Object Notation for efficient data transfer (~29% smaller than JSON)
- **Formatted Text Output**: Smart formatting for better readability including bold text, lists, and structured content
- **Chat History**: Keep track of previous questions for easy reference
- **Arabic NLP Support**: Optimized for Arabic text processing and normalization

---

## Team Members

| Name | Role |
|------|------|
| **Mostafa Ahmed Elgendy** | Developer |
| **Ahmed Ebrahim Elmesery** | Developer |
| **Hazem Gamal Riad** | Developer |
| **Mahmoud Ahmed Salah El-Din Abbas** | Developer |
| **Abdullah El-Sayed Saad Hafz** | Developer |
| **Hager Ayman Abdullah** | Developer |

### Supervisor
- **Mahmoud Radwan**

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | RESTful API server |
| **Data Format** | TOON Protocol | Token-Oriented Object Notation (29% lighter than JSON) |
| **Vector Database** | ChromaDB | Document embeddings storage |
| **Embeddings** | HuggingFace Transformers | Semantic text representation |
| **LLM** | Google Gemini 2.5 Flash | Text generation & QA |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript | Web interface with TOON support |
| **PDF Processing** | PyMuPDF | Document text extraction |
| **Framework** | LlamaIndex | Query engine & indexing |
| **Arabic Processing** | Custom NLP Pipeline | Text normalization & preprocessing |

### System Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   User Web Interface                    │
│              (HTML5, CSS3, Bootstrap 5, JS)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │   FastAPI Backend Server │
        │      (Port 8000)         │
        └──────────┬───────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
        ▼                      ▼
   ┌─────────────┐      ┌──────────────┐
   │ Upload PDF  │      │ Chat Engine  │
   │  Endpoint   │      │  Endpoint    │
   └─────────────┘      └──────┬───────┘
        │                      │
        ▼                      ▼
   ┌──────────────────────────────────┐
   │   LlamaIndex Query Engine        │
   │  (Document Processing & Search)  │
   └──────────────┬───────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
   ┌──────────────┐   ┌─────────────┐
   │  ChromaDB    │   │   Gemini    │
   │ (Embeddings) │   │    LLM      │
   └──────────────┘   └─────────────┘
```

---

## Project Structure

```
Constitution-Study-Chatbot/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── endpoint.py              # FastAPI endpoints (upload, chat)
│   ├── model.py                 # Gemini LLM & ChromaDB setup
│   ├── ingest.py                # PDF processing & indexing
│   ├── utils.py                 # Utility functions (Arabic text normalization)
│   ├── toon_parser.py           # TOON format parser & serializer
│   └── toon_middleware.py       # FastAPI middleware for TOON support
│
├── web/
│   ├── index.html               # Main web interface
│   ├── css/
│   │   └── style.css            # Application styling (Bootstrap 5 + custom)
│   └── js/
│       ├── app.js               # Frontend logic & TOON API integration
│       └── toon.js              # JavaScript TOON parser & serializer
│
├── data/
│   ├── constitution.pdf         # Egyptian Constitution document
│   └── chroma_db/               # Vector database storage
│
├── config/
│   ├── .env                     # Environment variables (API keys)
│   └── .env.example             # Example configuration
│
├── run_backend.py               # FastAPI server launcher
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **pip** or **conda** package manager
- **Google API Key** (for Gemini LLM)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

### Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/MostafaElgindy/depi-digital-legal-assistant.git
cd depi-digital-legal-assistant
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

1. Create or edit `config/.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

2. **Get your Google API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key and paste it in `.env`

#### Step 5: Verify Installation (Optional)
```bash
python startup.py
```

This will verify:
- ✅ Python version compatibility
- ✅ Required packages installation
- ✅ Environment variables configuration
- ✅ API connectivity

---

## Usage Guide

### Running the Application

The application requires **two separate servers** running on different ports:

#### Quick Start - Two Terminals Required

**Terminal 1 - Backend API Server (Port 8000):**
```bash
python run_backend.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Web Server (Port 8080):**
```bash
python run_web_server.py
```

Expected output:
```
Starting web server on http://127.0.0.1:8080
```

**Then open your browser to:** `http://127.0.0.1:8080`

#### Application Architecture

```
┌─────────────────────────────────────────┐
│        Web Browser                      │
│     http://127.0.0.1:8080              │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Web Server   │   │ API Backend  │
│ Port 8080    │   │ Port 8000    │
│ (Static)     │   │ (FastAPI)    │
└──────────────┘   └──────────────┘
   HTML/CSS/JS       REST API
```

#### Port Requirements

| Service | Port | Purpose |
|---------|------|---------|
| **Web Server** | 8080 | Static files (HTML, CSS, JS) |
| **API Backend** | 8000 | FastAPI endpoints (chat, upload) |

⚠️ **Important**: Both servers must be running simultaneously for the application to work.

#### Application Flow

```
1. Open Browser → http://127.0.0.1:8080
2. Frontend loads from Web Server (port 8080)
3. Frontend communicates with API (port 8000)
4. Upload Constitution PDF
5. Ask questions in Arabic
6. Receive AI-powered answers
7. Chat history maintained locally
```

### Using the Application

1. **Upload Constitution PDF**:
   - Click on the upload box or drag-and-drop the Constitution PDF
   - Wait for the processing to complete
   - You'll see: "تم تحميل الدستور بنجاح!" (Constitution loaded successfully!)

2. **Ask Questions** (Arabic Only):
   - Type your question **in Arabic** in the chat box
   - Press `Enter` or click the "Send" button
   - The AI will search the Constitution and provide an answer in Arabic
   - Messages automatically scroll to show the latest responses

3. **View History**:
   - Your recent questions appear in the left sidebar
   - Click on any previous question to restore it
   - Maximum of 10 questions are stored

### Supported Languages

⚠️ **Note**: The chatbot is optimized for **Arabic queries only**. 

For best results:
- ✅ Use Arabic text for questions
- ✅ Queries in Egyptian or Modern Standard Arabic both work
- ❌ English queries may not return accurate results
- ❌ Mixed Arabic-English text may cause issues

### Example Questions (Arabic)

- "ما هي حقوق العامل في الدستور المصري؟" (What are worker's rights?)
- "المادة 13 من الدستور" (Article 13 of the Constitution)
- "حقوق المرأة" (Women's rights)
- "تعريف العدالة الاجتماعية" (Definition of social justice)

---

## API Documentation

### Endpoints

#### 1. Upload PDF
```http
POST /upload_pdf/
Content-Type: multipart/form-data

Request:
- file: PDF file (max 50MB)

Response:
{
  "message": "PDF processed successfully",
  "documents_count": 42
}
```

#### 2. Chat Query
```http
GET /chat?query_request=your_question_here

Request Parameters:
- query_request (string): The question to ask

Response:
{
  "response": "Detailed answer from the Constitution...",
  "sources": "Constitution Article numbers"
}
```

### Example cURL Requests

```bash
# Upload PDF
curl -X POST "http://127.0.0.1:8000/upload_pdf/" \
  -F "file=@constitution.pdf"

# Chat Query
curl "http://127.0.0.1:8000/chat?query_request=ما%20هي%20حقوق%20الإنسان"
```

---

## TOON Protocol (Token-Oriented Object Notation)

This project uses **TOON** instead of traditional JSON for more efficient data transfer.

### What is TOON?

TOON is a lightweight, human-readable data format with the following benefits:

- **29% Smaller**: Reduces bandwidth usage compared to JSON
- **Comments Support**: Native support for `#` comments
- **Clean Syntax**: No unnecessary quotes for simple values
- **Faster Parsing**: Optimized parsing for real-time applications
- **Full Compatibility**: Seamlessly converts to/from JSON when needed

### TOON Examples

```toon
# Simple object
{
    name: "أحمد"
    age: 30
    active: true
}

# Array format
[1, 2, 3, "four", true, null]

# Nested structures
{
    user: {
        name: "سارة"
        email: "sara@example.com"
    }
    tags: ["python", "web", "ai"]
}
```

### API Responses in TOON

**Upload Response:**
```toon
{
    success: true
    message: "Collection created from 'constitution.pdf' successfully"
}
```

**Chat Response:**
```toon
{
    success: true
    response: "إجابتك من الدستور هنا..."
    message: "Query processed successfully"
}
```

### TOON Implementation

- **Backend**: `src/toon_parser.py` - Parser & Serializer
- **Frontend**: `web/js/toon.js` - JavaScript implementation
- **Middleware**: `src/toon_middleware.py` - Automatic conversion

For more information about TOON protocol, check the source code documentation.

---

This project demonstrates key AI/ML concepts essential for AI Engineers:

### 1. **Natural Language Processing (NLP)**
- **Arabic Text Normalization**: Handling diacritics and variant characters
- **Multilingual Support**: Processing both Arabic and English queries
- **Text Preprocessing**: Tokenization and semantic understanding

### 2. **Vector Embeddings & Semantic Search**
- **Sentence Transformers**: Converting text to high-dimensional vectors
- **Similarity Search**: Using cosine similarity for relevance matching
- **Embedding Model**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
- **Distance Metrics**: Finding semantically similar document chunks

### 3. **Vector Databases**
- **ChromaDB**: In-memory vector storage with persistence
- **Collection Management**: Organizing embeddings efficiently
- **Query Optimization**: Fast retrieval from millions of embeddings

### 4. **Retrieval-Augmented Generation (RAG)**
- **Document Chunking**: Breaking PDFs into manageable chunks
- **Context Retrieval**: Finding relevant passages for queries
- **Answer Generation**: Using LLM with retrieved context
- **Citation Mapping**: Connecting answers to source articles

### 5. **Large Language Models (LLMs)**
- **Model Integration**: Google Gemini API integration
- **Prompt Engineering**: Crafting effective prompts for QA tasks
- **Multilingual Generation**: Understanding and responding in Arabic/English
- **Context Window Management**: Handling token limits efficiently

### 6. **API Design & Architecture**
- **RESTful Endpoints**: Clean API design principles
- **Async Operations**: Non-blocking request handling
- **Error Handling**: Robust exception management
- **CORS Configuration**: Cross-origin resource sharing

### 7. **Full-Stack Development**
- **Backend Services**: FastAPI with Python
- **Frontend Integration**: Modern web UI with vanilla JS
- **File Processing**: PDF parsing and text extraction
- **Data Pipeline**: Upload → Process → Index → Query

---

### Key Technologies Explained

#### ChromaDB
- **Purpose**: Vector database for semantic search
- **Why**: Stores document embeddings for fast similarity search
- **Implementation**: In-memory storage with optional persistence

#### Google Gemini LLM
- **Model**: `models/gemini-2.5-flash`
- **Purpose**: Generate intelligent responses
- **Why**: Fast, accurate, and supports multilingual content

#### HuggingFace Embeddings
- **Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Purpose**: Convert text to numerical vectors
- **Why**: Supports Arabic and English, lightweight, and free

#### LlamaIndex
- **Purpose**: Query engine for document retrieval
- **Why**: Abstracts complexity of vector search and LLM integration

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Response Time | ~2-5 seconds |
| PDF Processing Time | ~10-30 seconds |
| Max File Size | 50 MB |
| Supported Languages | Arabic, English, 95+ languages |
| Vector Dimensions | 384 |
| Database Type | ChromaDB 0.3.21 |
| Data Format | TOON (29% smaller than JSON) |
| API Response Size | ~30-50% reduction vs JSON |

---

## Version

### Version 1.0.0 (November 2025)

**Constitution Study Chatbot** with TOON Protocol - Production Ready

Features:
- ✅ PDF upload and intelligent question-answering
- ✅ RAG-based retrieval with ChromaDB
- ✅ Google Gemini AI integration
- ✅ TOON Protocol for efficient data transfer (29% reduction vs JSON)
- ✅ Arabic & English NLP support
- ✅ Real-time chat interface

---

For production, consider:
- Use environment variables from secure vaults
- Implement authentication & authorization
- Enable HTTPS
- Add rate limiting
- Deploy behind reverse proxy (Nginx)
- Use PostgreSQL instead of in-memory ChromaDB

---

## Learning Outcomes

Through this project, AI Engineering students gain hands-on experience with:

- ✅ **Data Pipeline Development**: From raw documents to searchable vectors
- ✅ **Model Integration**: Working with external APIs (Google Gemini)
- ✅ **Vector Math**: Understanding embeddings and similarity metrics
- ✅ **Full-Stack Implementation**: Backend + Frontend integration
- ✅ **Production Best Practices**: Error handling, CORS, security
- ✅ **Arabic NLP**: Specific challenges in non-English language processing
- ✅ **API Development**: Building and consuming RESTful services
- ✅ **Performance Optimization**: Fast retrieval from vector databases
- ✅ **Deployment Considerations**: Scalability and production readiness

---

## License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## Acknowledgments

- **Digital Pioneer of Egypt** initiative for project inspiration

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅

---

Made with ❤️ by the Senior Project Team
