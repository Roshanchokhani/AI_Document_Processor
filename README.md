# AI-Powered Document Q&A Backend Service

A backend service that allows users to upload PDF documents and ask questions about them, receiving AI-generated answers based strictly on the document content.

## Features

- **PDF Upload**: Upload PDF documents (up to 10MB, recommended 3-5 pages)
- **Question Answering**: Ask natural language questions about the uploaded document
- **Answer Grounding**: AI responses are strictly based on document content - no hallucination
- **Interactive API Docs**: Auto-generated Swagger UI at `/docs`
- **FREE AI**: Uses Groq API (free tier - no payment required, super fast!)

## Tech Stack

- **Python 3.9+**
- **FastAPI** - Modern, high-performance web framework
- **Groq API** - Free and ultra-fast AI inference
- **PyPDF2** - PDF text extraction
- **Uvicorn** - ASGI server

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_Document_Processor
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your FREE Groq API Key

1. Go to: https://console.groq.com/keys
2. Sign up / Sign in (you can use Google account)
3. Click "Create API Key"
4. Copy the key

### 5. Configure Environment Variables

Edit the `.env` file and add your Groq API key:

```
GROQ_API_KEY=your_actual_api_key_here
```

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-14T12:00:00Z"
}
```

### Upload Document

```
POST /documents
Content-Type: multipart/form-data
```

**Request**: Upload a PDF file

**Response**:
```json
{
  "success": true,
  "message": "Document uploaded and processed successfully",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.pdf",
  "page_count": 3,
  "character_count": 5432
}
```

### Ask Question

```
POST /ask
Content-Type: application/json
```

**Request Body**:
```json
{
  "question": "What is the main topic of the document?"
}
```

**Response**:
```json
{
  "success": true,
  "question": "What is the main topic of the document?",
  "answer": "The document discusses...",
  "document_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing with cURL

### Upload a Document
```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@sample.pdf"
```

### Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

## Testing with Postman

1. **Upload Document**:
   - Method: POST
   - URL: `http://localhost:8000/documents`
   - Body: form-data
   - Key: `file` (type: File)
   - Value: Select your PDF file

2. **Ask Question**:
   - Method: POST
   - URL: `http://localhost:8000/ask`
   - Body: raw (JSON)
   - Content: `{"question": "Your question here"}`

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                         (main.py)                           │
├─────────────────────────────────────────────────────────────┤
│                         Routes                               │
│    POST /documents          POST /ask                        │
│         │                       │                            │
│         ▼                       ▼                            │
├─────────────────────────────────────────────────────────────┤
│                        Services                              │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ PDF Service  │  │Storage Service │  │   AI Service   │   │
│  │  (PyPDF2)    │  │  (In-Memory)   │  │    (Groq)      │   │
│  └──────────────┘  └────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Upload**:
   ```
   PDF File → Validation → Text Extraction → In-Memory Storage
   ```

2. **Question Answering**:
   ```
   Question → Retrieve Document → Build Prompt → Groq API → Grounded Answer
   ```

## Key Design Decisions

### 1. Service-Oriented Architecture
- **Decision**: Separate services for PDF, Storage, and AI operations
- **Reason**: Separation of concerns, easier testing, maintainable code
- **Trade-off**: More files, but better organization

### 2. In-Memory Storage
- **Decision**: Use Python dictionary for document storage
- **Reason**: Simple, fast, meets assignment requirements
- **Trade-off**: Data lost on restart (acceptable for this scope)
- **Future**: Could swap to SQLite or PostgreSQL easily

### 3. Answer Grounding via Prompt Engineering
- **Decision**: Use system prompt to constrain AI responses
- **Reason**: Prevents hallucination without complex retrieval systems
- **Implementation**:
  - Explicit instructions in system/user prompts
  - Low temperature (0.1) for focused responses
  - Required fallback message when answer not in document

### 4. Single Document Model
- **Decision**: Keep track of "current" document for simplicity
- **Reason**: Assignment focuses on single document Q&A
- **Future**: Could support multiple documents with document_id parameter

### 5. FastAPI Framework
- **Decision**: Use FastAPI over Flask
- **Reason**:
  - Automatic OpenAPI documentation
  - Built-in request validation
  - Modern async support
  - Type hints improve code quality

### 6. Groq API
- **Decision**: Use Groq for AI inference
- **Reason**:
  - FREE tier available (30 requests/minute)
  - No credit card required
  - Ultra-fast inference (LPU chips)
  - High quality Llama models
  - Easy to integrate

## Error Handling

The API handles these error cases:

| Error | HTTP Code | When |
|-------|-----------|------|
| Invalid file type | 400 | Non-PDF uploaded |
| Empty file | 400 | File has no content |
| File too large | 400 | Exceeds 10MB limit |
| PDF extraction failed | 400 | Cannot read PDF text |
| No document uploaded | 400 | /ask called before /documents |
| Question too long | 400 | Exceeds 1000 characters |
| API key missing | 500 | GROQ_API_KEY not set |
| Groq API error | 500 | Rate limit, network issues |
| Document too long | 500 | Token limit exceeded |

## Known Limitations

1. **Image-based PDFs**: Cannot extract text from scanned/image-only PDFs (would need OCR)
2. **Single Document**: Only one document active at a time
3. **In-Memory Storage**: Data lost on server restart
4. **Token Limits**: Very long documents may exceed model token limits
5. **No Authentication**: Anyone can upload and query (acceptable per requirements)
6. **Rate Limits**: Free Groq tier allows 30 requests per minute

## Project Structure

```
AI_Document_Processor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── documents.py     # API endpoint definitions
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py   # PDF text extraction
│       ├── storage_service.py # In-memory document storage
│       └── ai_service.py    # Groq API integration
├── .env                     # Environment variables (not committed)
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Future Improvements (Out of Scope)

- Database persistence (PostgreSQL/SQLite)
- Multiple document support with document selection
- OCR for image-based PDFs
- Caching for repeated questions
- Rate limiting
- Authentication/Authorization
- Document chunking for large files (RAG)
- Support for more file types (DOCX, TXT)
