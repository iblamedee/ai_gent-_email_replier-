# Project Structure

## Directory Layout

```
email-auto-responser/
├── app.py                          # FastAPI web application & REST API
├── main.py                         # CLI interface for the system
├── pyproject.toml                  # Project dependencies & metadata
├── README.md                       # Project overview
├── credentials.json                # Gmail OAuth2 credentials
├── token.json                      # Gmail API access token
│
├── features/                       # Feature modules
│   ├── retrivier/                  # Email retrieval & AI reply generation
│   │   ├── __init__.py            # Package initializer
│   │   ├── main.py                # Gmail API + LLM integration
│   │   └── main_1.ipynb           # Jupyter notebook for development
│   │
│   ├── sendmail/                   # Email sending functionality
│   │   └── send.py                # Gmail API email transmission
│   │
│   └── vector-db_rag/              # Vector database RAG (Retrieval Augmented Generation)
│       └── main.py                # Vector DB configuration & operations
│
├── queue/                          # Background job queue (Redis/RQ)
│   ├── docker-compose.yml          # Redis container configuration
│   └── worker.py                   # Background job processor
│
├── static/                         # Frontend static assets
│   └── style.css                   # UI styling (glassmorphism design)
│
└── templates/                      # HTML templates
    └── index.html                  # Main web interface
```

## Module Descriptions

### Core Application Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI web server with REST API endpoints for email operations |
| `main.py` | CLI interface for interactive email processing workflow |

### Feature Modules

#### `features/retrivier/` - Email Retrieval & AI Reply Generation
- **main.py**: Handles Gmail API integration and LLM-based reply generation using RAG
- **main_1.ipynb**: Development notebook for experimenting with retrieval and generation logic

#### `features/sendmail/` - Email Sending
- **send.py**: Sends email replies via Gmail API with base64 encoding

#### `features/vector-db_rag/` - Vector Database & RAG
- **main.py**: Vector database setup and similarity search for context retrieval

### Infrastructure

#### `queue/` - Background Job Processing
- **worker.py**: RQ worker for processing background jobs
- **docker-compose.yml**: Redis container setup for job queue

### Frontend

#### `static/` - Static Assets
- **style.css**: Glassmorphism UI styling

#### `templates/` - HTML Templates
- **index.html**: Main web interface with chat-like UI

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python dependencies and project metadata |
| `credentials.json` | Gmail OAuth2 application credentials |
| `token.json` | Gmail API user access token |

## Application Flow

### Web API Flow (`app.py`)
```
User Frontend
    ↓
FastAPI App (app.py)
    ├─→ /api/fetch-email → fetch_gmail()
    ├─→ /api/generate-reply → get_query()
    ├─→ /api/send-email → send_mail()
    └─→ /api/mark-read → mark_read()
    ↓
Gmail API
```

### CLI Flow (`main.py`)
```
User Input (CLI)
    ↓
get_result()
    ├─→ fetch_gmail() → Get unread email
    ├─→ get_query() → Generate AI reply
    ├─→ User confirmation prompt
    └─→ send_mail() → Send email
```

### AI Reply Generation Flow
```
Email Input
    ↓
Vector Database Similarity Search
    ↓
Context Retrieval (RAG)
    ↓
LLM Processing with System Prompt
    ↓
Generated Reply Output
```
