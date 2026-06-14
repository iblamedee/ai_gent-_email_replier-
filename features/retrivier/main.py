#!/usr/bin/env python
# coding: utf-8
"""
Email Retrieval & AI Reply Generation Module
=============================================

Handles:
  - Fetching unread emails from Gmail via Gmail API
  - Extracting sender email and message ID
  - Generating AI-powered replies using LLM with RAG (Retrieval Augmented Generation)
  - Marking emails as read
  - Vector-based similarity search for context retrieval

Dependencies:
  - Google Gmail API
  - LangChain for vector operations
  - OpenRouter AI API for LLM calls
  - Qdrant for vector database
"""

# ============================================================================
# Imports
# ============================================================================
import os
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import base64
from email.utils import parseaddr
from pathlib import Path
from dotenv import load_dotenv



# ============================================================================
# Gmail API Configuration
# ============================================================================
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")

# Authenticate with Gmail API using saved OAuth2 credentials
creds = Credentials.from_authorized_user_file(
    str(TOKEN_PATH),
    SCOPES
)

# Initialize Gmail API service
gmail_service = build("gmail", "v1", credentials=creds)

# ============================================================================
# Email Retrieval Functions
# ============================================================================

def fetch_gmail(gmail_service):
    """
    Fetch the first unread email from Gmail inbox.
    
    Workflow:
        1. Query Gmail API for unread emails in primary category
        2. Extract message ID from first unread email
        3. Retrieve full message details using message ID
        4. Parse email headers to extract sender address
        5. Decode email body (base64 URL-safe format)
        6. Extract plain text content from message
    
    Args:
        gmail_service: Authenticated Gmail API service instance
        
    Returns:
        tuple: (email_text, sender_email, message_id) if unread email found
        None: If no unread emails in inbox
    """
    # ========== Query for Unread Emails ==========
    results = gmail_service.users().messages().list(
        userId="me",
        q="category:primary is:unread",  # Only primary category, unread emails
        maxResults=1  # Get only the first unread email
    ).execute()

    data = results.get("messages", [])
    print(data)

    if not data:
        return None
    
    # ========== Extract Message ID ==========
    message_id = data[0]["id"]

    # ========== Retrieve Full Message ==========
    message = gmail_service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    # ========== Extract Sender Email ==========
    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    sender_email = parseaddr(
        next(
            header["value"]
            for header in headers
            if header["name"] == "From"
        )
    )[1]

    # ========== Extract Email Body ==========
    parts = payload.get("parts", [])
    text = ""

    for part in parts:
        if part.get("mimeType") == "text/plain":
            message_content = part.get("body", {}).get("data")

            if message_content:
                # Decode from base64 URL-safe format
                decode_message = base64.urlsafe_b64decode(message_content)
                text = decode_message.decode("utf-8")
                break

    return text, sender_email, message_id


def mark_read(message_id: str):
    """
    Mark an email as read in Gmail.
    
    Removes the UNREAD label from the specified message.
    
    Args:
        message_id (str): Gmail message ID to mark as read
        
    Returns:
        str: Confirmation message
    """
    gmail_service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()

    return f"Mark as read sucessfully"



# ============================================================================
# LLM & Vector Database Configuration
# ============================================================================

load_dotenv()

# Initialize OpenRouter LLM client
# Uses OpenRouter API as proxy for various LLM models
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Initialize embeddings model for vector representation
# Uses Perplexity embeddings for semantic similarity
embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="perplexity/pplx-embed-v1-0.6b",
    check_embedding_ctx_length=False,
)

# Connect to Qdrant vector database for similarity search
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="company-database",
    embedding=embeddings,
    validate_collection_config=False,
)

# ============================================================================
# AI Reply Generation with RAG (Retrieval Augmented Generation)
# ============================================================================

def get_query(email: str):
    """
    Generate an AI-powered email reply using RAG (Retrieval Augmented Generation).
    
    Process:
        1. Search vector database for similar documents related to email content
        2. Retrieve top matching results as context
        3. Create system prompt with company knowledge context
        4. Send email + context to LLM for generating professional reply
        5. Return generated reply text
    
    Behavior:
        - Replies only based on provided company database context
        - Refers unknown queries to support team
        - Flags emails with many links as potential spam
    
    Args:
        email (str): Email content to generate a reply for
        
    Returns:
        str: AI-generated professional email reply
    """
    # ========== Vector Similarity Search ==========
    # Find related documents in vector database based on email content
    search_result = vector_db.similarity_search(query=email)

    # ========== Build Context from Search Results ==========
    context = "\n\n\n".join(
        [f"page_content:{result.page_content}" for result in search_result]
    )

    # ========== Create System Prompt ==========
    # Defines LLM behavior and provides company knowledge context
    system_prompt = f"""You are a professional email responser agent that give reply to mails
    only from provided context

    if mail doesn't belong from or relate from context then say i will share this with support team, Be paitent

    and if the mail have too many link reply that as spam

    context: {context}
    """

    # ========== Call LLM for Reply Generation ==========
    responser = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": email},
        ]
    )

    return responser.choices[0].message.content










