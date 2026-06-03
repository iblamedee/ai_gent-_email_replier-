from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from pathlib import Path
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")




def send_mail(gmail_service, sender_mail, reply: str):

    message = MIMEText(reply)

    message["to"] = sender_mail
    message["subject"] = "Re: Reply your email"

    encode_reply = message.as_bytes()
    raw_message = base64.urlsafe_b64encode(encode_reply).decode()

    gmail_service.users().messages().send(
        userId = "me",
        body = {"raw": raw_message},
        
    ).execute()

    print("Email sent sucessfully")