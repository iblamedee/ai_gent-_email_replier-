"""
AI Email Auto-Responder - FastAPI Backend
==========================================

Main application module for the AI-powered email auto-responder system.
Provides REST API endpoints for:
  - Fetching unread emails from Gmail
  - Generating AI-powered replies
  - Sending email responses
  - Marking emails as read
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from features.retrivier.main import get_query, fetch_gmail, mark_read, gmail_service
from features.sendmail.send import send_mail

# ============================================================================
# FastAPI Application Setup
# ============================================================================
app = FastAPI(title="AI Agent for COSTUMER SUPPORT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================================
# Request/Response Models
# ============================================================================

class ReplyRequest(BaseModel):
    """Request body for AI reply generation endpoint."""
    email_content: str

class SendRequest(BaseModel):
    """Request body for sending email endpoint."""
    recipient_email: str
    reply_content: str

class MarkReadRequest(BaseModel):
    """Request body for marking email as read endpoint."""
    message_id: str

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def index():
    """
    Serve the main HTML interface.
    
    Returns:
        FileResponse: The main index.html page
    """
    return FileResponse("templates/index.html")

@app.get("/api/fetch-email")
async def fetch_email():
    """
    Fetch the next unread email from Gmail inbox.
    
    Returns:
        dict: Contains email content, sender email, and message ID if available,
              or error message if no unread emails found
    """
    result = fetch_gmail(gmail_service)
    if not result:
        return {"success": False, "message": "No email found"}
    email_text, sender, message_id = result
    return {
        "success": True,
        "email_content": email_text,
        "sender_email": sender,
        "message_id": message_id
    }

@app.post("/api/generate-reply")
async def generate_reply(request: ReplyRequest):
    """
    Generate an AI-powered reply for the given email content.
    
    Args:
        request (ReplyRequest): Email content to generate a reply for
        
    Returns:
        dict: Generated reply text
        
    Raises:
        HTTPException: If email content is empty
    """
    if not request.email_content.strip():
        raise HTTPException(status_code=400, detail="Email content is required")
    answer = get_query(request.email_content)
    return {"success": True, "reply": answer}

@app.post("/api/send-email")
async def send_email(request: SendRequest):
    """
    Send an email reply to the specified recipient.
    
    Args:
        request (SendRequest): Recipient email and reply content
        
    Returns:
        dict: Success confirmation message
        
    Raises:
        HTTPException: If recipient or reply content is empty
    """
    if not request.recipient_email.strip() or not request.reply_content.strip():
        raise HTTPException(status_code=400, detail="Recipient and reply content are required")
    send_mail(gmail_service, request.recipient_email, request.reply_content)
    return {"success": True, "message": "Email sent"}

@app.post("/api/mark-read")
async def mark_email_read(request: MarkReadRequest):
    """
    Mark an email as read in Gmail.
    
    Args:
        request (MarkReadRequest): Message ID to mark as read
        
    Returns:
        dict: Success confirmation message
        
    Raises:
        HTTPException: If message ID is empty
    """
    if not request.message_id.strip():
        raise HTTPException(status_code=400, detail="Message ID is required")
    mark_read(request.message_id)
    return {"success": True, "message": "Email marked as read"}
