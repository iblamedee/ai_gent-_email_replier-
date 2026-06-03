#!/usr/bin/env python
# coding: utf-8

# In[80]:


import os
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import base64
from email.utils import parseaddr

# In[81]:


from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


TOKEN_PATH = Path(r"x:\project\email-auto-responser\token.json")

creds = Credentials.from_authorized_user_file(
    str(TOKEN_PATH),
    SCOPES
)


# In[82]:


gmail_service = build("gmail", "v1", credentials=creds)

def fetch_gmail(gmail_service):

    results = gmail_service.users().messages().list(
        userId="me",
        q="category:primary is:unread",
        maxResults=1
    ).execute()


    data = results.get("messages", [])
    # return fetch_gmail(gmail_service)
    print(data)

    if not data:
        return None
    
    message_id = data[0]["id"]


    message = gmail_service.users().messages().get(
        userId="me",
        id=message_id,
        format ="full"
    ).execute()

    payload = message.get("payload", {})

    headers = payload.get("headers", [])

    sender_email = parseaddr(
            next(
            header["value"]
            for header in headers
            if header["name"] == "From"
        )
    )[1]

    parts = payload.get("parts", [])

    text = ""

    for part in parts:
        if part.get("mimeType") == "text/plain":
            message_content = part.get("body", {}).get("data")

            if message_content:
                decode_message = base64.urlsafe_b64decode(message_content)
                text = decode_message.decode("utf-8")




                break


    return text , sender_email, message_id


def mark_read(message_id:str):
    gmail_service.users().messages().modify(
        userId="me",
        id=message_id,
        body= {
            "removeLabelIds": ["UNREAD"]
        }
    ).execute()

    return f"Mark as read sucessfully"
# In[83]:



# In[97]:


from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="perplexity/pplx-embed-v1-0.6b",
    check_embedding_ctx_length=False,
)


# In[99]:


vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="company-database",
    embedding=embeddings,
    validate_collection_config=False,
)


# In[ ]:


def get_query(email: str):

    search_result = vector_db.similarity_search(
        query=email)


    context = "\n\n\n".join([f"""
        page_content:{result.page_content}"""
        for result in search_result
        ])

    system_prompt = f"""You are a professional email responser agent that give reply to mails
    only from provided context

    if mail doesn't belong from or relate from context then say i will share this with support team, Be paitent

    and if the mail have too many link reply that as spam


    context: {context}
    """

    responser = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[

            {"role":"system", "content": system_prompt},
            {"role":"user", "content": email},

            ]

    )

    return responser.choices[0].message.content










