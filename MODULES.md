# Module Documentation

## Table of Contents
1. [app.py - FastAPI Application](#apppy)
2. [main.py - CLI Interface](#mainpy)
3. [features/retrivier/main.py - Email & AI](#retriviermain)
4. [features/sendmail/send.py - Email Sending](#sendmailsend)

---

## app.py

**Purpose**: FastAPI web application with REST API endpoints

**Key Components**:

### Imports & Setup
```python
# FastAPI framework with CORS support
# Static file serving for CSS/JS
# Load environment variables from .env
```

### Middleware Configuration
- **CORS Middleware**: Allows cross-origin requests from all origins
  - `allow_origins=["*"]`
  - `allow_credentials=True`
  - `allow_methods=["*"]`
  - `allow_headers=["*"]`

### Static Files
- Mounts `/static` directory for CSS, JavaScript, images

### Request Models

#### ReplyRequest
```python
class ReplyRequest(BaseModel):
    email_content: str  # Email text to generate reply for
```

#### SendRequest
```python
class SendRequest(BaseModel):
    recipient_email: str   # Email address to send to
    reply_content: str     # Email body content
```

#### MarkReadRequest
```python
class MarkReadRequest(BaseModel):
    message_id: str  # Gmail message ID
```

### API Endpoints

#### GET `/`
- **Purpose**: Serve main HTML interface
- **Returns**: `FileResponse` with `index.html`

#### GET `/api/fetch-email`
- **Purpose**: Fetch next unread email from Gmail
- **Returns**: 
  ```json
  {
    "success": boolean,
    "email_content": string,
    "sender_email": string,
    "message_id": string
  }
  ```
- **Error Response**: `{"success": false, "message": "No email found"}`

#### POST `/api/generate-reply`
- **Purpose**: Generate AI-powered reply for email content
- **Request**: `ReplyRequest` with email_content
- **Returns**:
  ```json
  {
    "success": true,
    "reply": string  # AI-generated reply
  }
  ```
- **Validation**: Email content must not be empty
- **Status Code**: 400 if validation fails

#### POST `/api/send-email`
- **Purpose**: Send generated reply to recipient
- **Request**: `SendRequest` with recipient_email and reply_content
- **Returns**: `{"success": true, "message": "Email sent"}`
- **Validation**: Both recipient_email and reply_content must not be empty
- **Status Code**: 400 if validation fails

#### POST `/api/mark-read`
- **Purpose**: Mark email as read in Gmail
- **Request**: `MarkReadRequest` with message_id
- **Returns**: `{"success": true, "message": "Email marked as read"}`
- **Validation**: message_id must not be empty
- **Status Code**: 400 if validation fails

---

## main.py

**Purpose**: Command-line interface for interactive email processing

**Dependencies**:
- `features.retrivier.main`: Email retrieval and AI reply generation
- `features.sendmail.send`: Email transmission
- `dotenv`: Environment variable loading

### Functions

#### get_result()
```python
def get_result() -> str
```

**Purpose**: Main workflow for processing emails with user interaction

**Workflow**:
1. **Fetch Email**: Get next unread email from Gmail
2. **Handle No Email**: Return if inbox is empty
3. **Display Email**: Print email content and sender
4. **Generate Reply**: Use AI to generate professional response
5. **Display Reply**: Print generated reply to user
6. **Get Confirmation**: Prompt user for yes/no confirmation
7. **Send or Cancel**: Send email if confirmed, otherwise skip

**Returns**: Generated reply string or "there is no mail"

**User Input**: Interactive prompt asking "Should send this mail ? (yes/no):"

**Side Effects**:
- Prints email information to console
- Prints generated reply to console
- Sends email via Gmail API if user confirms
- Prints confirmation/cancellation message

**Error Handling**: Gracefully handles no unread emails

---

## features/retrivier/main.py

**Purpose**: Email retrieval from Gmail and AI reply generation with RAG

**Key Features**:
- Gmail API integration for email fetching
- Vector database for knowledge retrieval
- LLM integration for intelligent reply generation
- Base64 encoding/decoding for email message handling

### Configuration

#### Gmail Settings
```python
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")
```
- Uses OAuth2 credentials from `token.json`
- Requires `GMAIL_MODIFY` scope

#### LLM Configuration
```python
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
model = "gpt-5-nano"
```
- Uses OpenRouter as LLM provider
- Requires `OPENROUTER_API_KEY` environment variable

#### Vector Database
```python
url = "http://localhost:6333"  # Qdrant server
collection_name = "company-database"
embedding_model = "perplexity/pplx-embed-v1-0.6b"
```
- Connects to local Qdrant instance
- Uses Perplexity embeddings for similarity search

### Functions

#### fetch_gmail(gmail_service)
```python
def fetch_gmail(gmail_service) -> tuple[str, str, str] | None
```

**Purpose**: Fetch the first unread email from Gmail inbox

**Parameters**:
- `gmail_service`: Authenticated Gmail API service instance

**Returns**:
- Success: `(email_text, sender_email, message_id)` tuple
- Failure: `None` if no unread emails

**Process**:
1. Query Gmail API for unread emails in primary category
2. Get first unread message ID
3. Retrieve full message details (headers and body)
4. Parse sender email from "From" header
5. Decode base64 message body
6. Extract plain text content

**Error Handling**: Returns `None` if no unread emails found

**Gmail Query Filter**: `"category:primary is:unread"` (primary inbox, unread only)

---

#### mark_read(message_id)
```python
def mark_read(message_id: str) -> str
```

**Purpose**: Mark a Gmail message as read

**Parameters**:
- `message_id` (str): Gmail message ID to mark as read

**Returns**: Confirmation message string

**Operation**: Removes `UNREAD` label from the message

**Side Effect**: Updates Gmail message status via API

---

#### get_query(email)
```python
def get_query(email: str) -> str
```

**Purpose**: Generate AI-powered email reply using RAG (Retrieval Augmented Generation)

**Parameters**:
- `email` (str): Email content to generate reply for

**Returns**: AI-generated professional email reply (string)

**RAG Pipeline**:
1. **Vector Search**: Search company knowledge base for relevant documents
   - Uses cosine similarity to find top matching documents
   - Documents from `company-database` collection

2. **Context Building**: Combine all matching documents as context
   - Joins documents with triple newlines
   - Formats as: `page_content: <document_content>`

3. **System Prompt**: Creates instructions for LLM
   - Tells LLM to only reply based on provided context
   - Instructions to escalate unknown queries to support team
   - Spam detection for emails with many links

4. **LLM Call**: Sends to OpenRouter LLM
   - System role: Context and behavior instructions
   - User role: The email to reply to
   - Model: gpt-5-nano

5. **Response Extraction**: Returns LLM generated message content

**Example System Prompt**:
```
You are a professional email responser agent that give reply to mails
only from provided context

if mail doesn't belong from or relate from context then say i will share 
this with support team, Be paitent

and if the mail have too many link reply that as spam

context: [company knowledge base documents]
```

**Behavior**:
- ✅ Replies professionally based on company knowledge
- ✅ Escalates out-of-scope queries to support team
- ✅ Detects and flags spam (multiple links)
- ❌ Does not invent information outside context

---

## features/sendmail/send.py

**Purpose**: Send email replies via Gmail API

**Gmail Settings**:
```python
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")
```

### Functions

#### send_mail(gmail_service, sender_mail, reply)
```python
def send_mail(gmail_service, sender_mail: str, reply: str) -> None
```

**Purpose**: Send an email reply to a recipient

**Parameters**:
- `gmail_service`: Authenticated Gmail API service instance
- `sender_mail` (str): Recipient email address
- `reply` (str): Email body content

**Returns**: None

**Side Effects**: 
- Sends email via Gmail API
- Prints "Email sent sucessfully" confirmation

**Email Properties**:
- **To**: Recipient email (from `sender_mail` parameter)
- **Subject**: "Re: Reply your email"
- **Body**: Generated reply content
- **Format**: Plain text MIME message

**Encoding Process**:
1. Create MIME text message with reply content
2. Set recipient and subject
3. Convert to bytes
4. Encode in base64 URL-safe format (Gmail API requirement)
5. Send via Gmail API

**Gmail API Operation**: `users().messages().send()`

---

## Environment Variables Required

Create `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key  # For embeddings
OPENROUTER_API_KEY=your_openrouter_key  # For LLM
```

## External Services

| Service | Purpose | Configuration |
|---------|---------|----------------|
| Gmail API | Email retrieval and sending | OAuth2 (credentials.json, token.json) |
| OpenRouter | LLM provider | API key in .env |
| Qdrant | Vector database | http://localhost:6333 |
