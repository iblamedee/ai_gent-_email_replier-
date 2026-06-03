from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from features.retrivier.main import get_query, fetch_gmail, mark_read, gmail_service
from features.sendmail.send import send_mail

app = FastAPI(title="AI Agent for COSTUMER SUPPORT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ReplyRequest(BaseModel):
    email_content: str

class SendRequest(BaseModel):
    recipient_email: str
    reply_content: str

class MarkReadRequest(BaseModel):
    message_id: str

@app.get("/")
async def index():
    return FileResponse("templates/index.html")

@app.get("/api/fetch-email")
async def fetch_email():
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
    if not request.email_content.strip():
        raise HTTPException(status_code=400, detail="Email content is required")
    answer = get_query(request.email_content)
    return {"success": True, "reply": answer}

@app.post("/api/send-email")
async def send_email(request: SendRequest):
    if not request.recipient_email.strip() or not request.reply_content.strip():
        raise HTTPException(status_code=400, detail="Recipient and reply content are required")
    send_mail(gmail_service, request.recipient_email, request.reply_content)
    return {"success": True, "message": "Email sent"}

@app.post("/api/mark-read")
async def mark_email_read(request: MarkReadRequest):
    if not request.message_id.strip():
        raise HTTPException(status_code=400, detail="Message ID is required")
    mark_read(request.message_id)
    return {"success": True, "message": "Email marked as read"}
