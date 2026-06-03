# AI Email Auto-Responder

An intelligent AI-powered email auto-responder system with a beautiful glassmorphism UI built with FastAPI.

## Features

- 📧 **AI-Powered Responses** - Generate intelligent email replies using LangChain and OpenAI
- 🎨 **Glassmorphism UI** - Beautiful, modern interface with white and grey color scheme
- 📊 **Email Management** - Fetch, read, and automatically respond to emails via Gmail
- 🔐 **Secure** - Uses OAuth 2.0 for secure Gmail authentication
- 💬 **Interactive Chat** - Chat interface to interact with the AI assistant
- ⚡ **FastAPI Backend** - Fast and modern async Python web framework

## Setup

### Prerequisites

- Python 3.13+
- Gmail account with API access
- OpenAI API key

### Installation

1. Install dependencies:
```bash
pip install -e .
```

Or if using uv:
```bash
uv sync
```

2. Create a `.env` file in the root directory with your credentials:
```
OPENAI_API_KEY=your_key_here
```

3. Set up Gmail API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download and save as `credentials.json` in the project root

## Running the Application

### Start the FastAPI Server

```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --port 8000
```

The server will start on `http://localhost:8000`

Open your browser and navigate to `http://localhost:8000` to access the UI.

### Features in the UI

**Chat Interface:**
- Type messages to interact with the AI assistant
- Press Enter or click Send button to send messages

**Fetch Emails:**
- Click "Fetch Emails" to retrieve your latest email
- View email preview in a modal
- Option to generate an AI reply

**Generate Reply:**
- Paste email content manually
- AI generates an intelligent response
- Review and send the reply

**Clear Conversation:**
- Clear chat history with one click
- Starts a fresh conversation

## Project Structure

```
.
├── app.py                          # FastAPI application
├── main.py                         # Core email logic (legacy CLI)
├── credentials.json                # Gmail API credentials
├── token.json                      # Gmail authentication token
├── pyproject.toml                  # Project dependencies
├── templates/
│   └── index.html                  # Main UI template
├── static/
│   └── style.css                   # Glassmorphism styles
├── features/
│   ├── retrivier/
│   │   ├── __init__.py
│   │   ├── main.py                 # Email retrieval logic
│   │   └── main_1.ipynb           # Jupyter notebook
│   ├── sendmail/
│   │   └── send.py                 # Email sending logic
│   └── vector-db_rag/
│       └── main.py                 # RAG implementation
└── queue/
    ├── docker-compose.yml          # Redis queue setup
    └── worker.py                   # Background job worker
```

## API Endpoints

- `GET /` - Serve the main UI
- `POST /api/chat` - Send a chat message
  - Request: `{"message": "your message"}`
  - Response: `{"response": "AI response", "history": [...]}`

- `GET /api/fetch-emails` - Fetch latest email
  - Response: `{"success": true, "email_content": "...", "sender_email": "..."}`

- `POST /api/generate-reply` - Generate AI reply for email content
  - Request: `{"email_content": "email text"}`
  - Response: `{"reply": "generated reply"}`

- `POST /api/send-email` - Send email reply
  - Request: `{"recipient_email": "...", "reply_content": "..."}`
  - Response: `{"success": true, "message": "Email sent successfully"}`

- `GET /api/conversation` - Get conversation history
  - Response: `{"history": [...]}`

- `POST /api/clear-conversation` - Clear conversation history
  - Response: `{"success": true}`

## Technologies Used

- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** FastAPI, Uvicorn
- **AI:** LangChain, OpenAI GPT
- **Email:** Gmail API
- **Vector DB:** Qdrant
- **Task Queue:** RQ (Redis Queue)
- **UI Style:** Glassmorphism

## License

MIT
