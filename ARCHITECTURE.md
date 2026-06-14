# System Architecture

## Overview

AI Email Auto-Responder is an intelligent system that automatically generates and sends professional email replies using AI, powered by:
- **Gmail API** for email management
- **LangChain + OpenRouter** for AI-powered reply generation
- **Qdrant Vector Database** for knowledge retrieval (RAG)
- **FastAPI** for the REST API backend
- **Redis + RQ** for background job processing

## System Components

### 1. Email Retrieval Layer (`features/retrivier/`)

**Responsibility**: Fetch unread emails from Gmail and manage message status

**Components**:
- `fetch_gmail()`: Retrieves unread emails with sender and message ID
- `mark_read()`: Marks processed emails as read

**Gmail API Integration**:
```
Gmail API Service
    ↓
Query: category:primary is:unread
    ↓
Parse Message Headers (From, Subject)
    ↓
Decode Base64 Message Body
    ↓
Return: (email_text, sender_email, message_id)
```

### 2. AI Reply Generation Layer (`features/retrivier/`)

**Responsibility**: Generate intelligent, context-aware email replies

**Pipeline**:
```
Input Email
    ↓
Vector Similarity Search (Qdrant)
    ↓
Retrieve Relevant Context Documents
    ↓
Create RAG System Prompt
    ↓
Call OpenRouter LLM (GPT-5-nano)
    ↓
Output: AI-Generated Reply
```

**RAG (Retrieval Augmented Generation)**:
- Uses company knowledge base from vector database
- Generates replies only based on provided context
- Falls back to "contact support" for out-of-scope queries

**LLM Behavior**:
- Replies professionally based on company context
- Handles spam detection (multiple links)
- Escalates unknown queries to support team

### 3. Email Sending Layer (`features/sendmail/`)

**Responsibility**: Send generated replies via Gmail API

**Flow**:
```
Generated Reply Text
    ↓
Create MIME Email Message
    ↓
Encode in Base64 (Gmail API requirement)
    ↓
Send via Gmail API
    ↓
Confirmation Message
```

### 4. Vector Database Layer (`features/vector-db_rag/`)

**Configuration**:
- **Database**: Qdrant (vector DB)
- **Embeddings**: Perplexity embeddings (pplx-embed-v1-0.6b)
- **Connection**: `http://localhost:6333`
- **Collection**: `company-database`

**Purpose**: Store and search company knowledge for context-aware replies

### 5. API Layer (`app.py`)

**Framework**: FastAPI with CORS middleware

**Endpoints**:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve main HTML interface |
| GET | `/api/fetch-email` | Fetch next unread email |
| POST | `/api/generate-reply` | Generate AI reply for email content |
| POST | `/api/send-email` | Send email to recipient |
| POST | `/api/mark-read` | Mark email as read in Gmail |

**Request/Response Models**:
- `ReplyRequest`: `{email_content: str}`
- `SendRequest`: `{recipient_email: str, reply_content: str}`
- `MarkReadRequest`: `{message_id: str}`

### 6. CLI Layer (`main.py`)

**Purpose**: Interactive command-line interface for email processing

**Workflow**:
1. Fetch unread email from Gmail
2. Generate AI reply
3. Display reply to user
4. Request user confirmation
5. Send email if approved

### 7. Frontend (`templates/index.html`, `static/style.css`)

**Design**: Glassmorphism UI with white and grey color scheme

**Features**:
- Email fetching interface
- Real-time reply generation
- Email preview and editing
- Send/cancel actions

## Data Flow Diagrams

### Complete Email Processing Flow

```
┌─────────────┐
│ Gmail Inbox │
└──────┬──────┘
       │ (unread email)
       ↓
┌──────────────────────┐
│ fetch_gmail()        │ Gmail API
│ - Query unread       │
│ - Parse headers      │
│ - Decode body        │
└──────────┬───────────┘
           │ (email_text, sender, message_id)
           ↓
┌──────────────────────┐
│ get_query()          │
│ - Vector search      │ Qdrant DB + OpenRouter LLM
│ - Build context      │
│ - Call LLM           │
└──────────┬───────────┘
           │ (generated_reply)
           ↓
┌──────────────────────┐
│ send_mail()          │ Gmail API
│ - Create MIME msg    │
│ - Encode B64         │
│ - Send email         │
└──────────┬───────────┘
           │
           ↓
┌─────────────┐
│ Recipient   │
└─────────────┘
```

### API Request Processing

```
HTTP Request
    ↓
FastAPI Route Handler
    ↓
Validate Request Model
    ↓
Call Feature Function
    ├─→ fetch_gmail()
    ├─→ get_query()
    ├─→ send_mail()
    └─→ mark_read()
    ↓
Return JSON Response
    ↓
HTTP Response
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI + Uvicorn | REST API server |
| Email | Gmail API | Email retrieval & sending |
| AI/LLM | OpenRouter + GPT-5-nano | Reply generation |
| Embeddings | Perplexity (pplx-embed-v1-0.6b) | Vector embeddings |
| Vector DB | Qdrant | Knowledge storage & retrieval |
| Job Queue | Redis + RQ | Background processing |
| Frontend | HTML + CSS | Web interface |
| Python | 3.13+ | Core language |

## Authentication & Security

- **Gmail API**: OAuth2 with `credentials.json` and `token.json`
- **LLM API**: OpenRouter API key from environment variables
- **CORS**: Enabled for frontend-backend communication
- **Request Validation**: Pydantic models for type safety

## Error Handling

- **No unread emails**: Returns appropriate error message
- **Missing email content**: Returns 400 Bad Request
- **API failures**: HTTP exceptions with descriptive messages
- **Out of scope queries**: LLM escalates to support team

## Performance Considerations

- **Email fetching**: Single unread email per request (optimized)
- **Vector search**: Efficient similarity search with Qdrant
- **LLM latency**: Depends on OpenRouter LLM response time
- **Background jobs**: Optional RQ worker for async processing

## Future Enhancements

- [ ] Batch email processing
- [ ] Email templates customization
- [ ] Support for multiple email accounts
- [ ] Advanced spam filtering
- [ ] Reply quality metrics and feedback loop
- [ ] Multi-language support
