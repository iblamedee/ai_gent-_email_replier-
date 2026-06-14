"""
Email Sending Module
====================

Handles sending automated email replies via Gmail API.
Encodes emails in base64 format as required by Gmail API.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from pathlib import Path
import base64

# ============================================================================
# Gmail Configuration
# ============================================================================
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")


def send_mail(gmail_service, sender_mail, reply: str):
    """
    Send an email reply via Gmail API.
    
    Constructs a MIME email message, encodes it in base64 format,
    and sends it through the Gmail API.
    
    Args:
        gmail_service: Authenticated Gmail API service instance
        sender_mail (str): Recipient email address
        reply (str): Email body content to send
        
    Returns:
        None
        
    Side Effects:
        Sends email via Gmail API and prints confirmation message
    """
    # ========== Create MIME Message ==========
    message = MIMEText(reply)
    message["to"] = sender_mail
    message["subject"] = "Re: Reply your email"

    # ========== Encode Message ==========
    encode_reply = message.as_bytes()
    raw_message = base64.urlsafe_b64encode(encode_reply).decode()

    # ========== Send via Gmail API ==========
    gmail_service.users().messages().send(
        userId = "me",
        body = {"raw": raw_message},
    ).execute()

    print("Email sent sucessfully")