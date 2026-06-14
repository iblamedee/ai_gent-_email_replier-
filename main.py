"""
AI Email Auto-Responder - CLI Interface
========================================

Command-line interface for the AI-powered email auto-responder.
Allows users to fetch unread emails, generate AI replies, and send responses
with manual confirmation before sending.
"""

from dotenv import load_dotenv
load_dotenv()
from features.retrivier.main import get_query, fetch_gmail, gmail_service
from features.sendmail.send import send_mail






def get_result():
    """
    Main workflow: Fetch email, generate AI reply, and send with user confirmation.
    
    Workflow:
        1. Fetch unread email from Gmail inbox
        2. Generate AI-powered response using LLM
        3. Display reply to user for review
        4. Request user confirmation before sending
        5. Send email or cancel based on user input
    
    Returns:
        str: Generated reply text, or "there is no mail" if no unread emails
    """
    # ========== STEP 1: Fetch Email ==========
    result = fetch_gmail(gmail_service)

    if not result:
        return f"there is no mail"
    
    text, sender_mail = result
    
    # ========== STEP 2: Display Email Info ==========
    print(f"email:{text}")
    print(f"send mail:{sender_mail}")

    # ========== STEP 3: Generate AI Reply ==========
    reply = get_query(text)
    print(f"\n\n Gnerated reply:")
    print(reply)

    # ========== STEP 4: Get User Confirmation ==========
    choose = input("\n Should send  this mail ? (yes/no): ").strip().lower()
    if choose in ["yes", "y"]:
        # ========== STEP 5: Send Email ==========
        send_mail(
            gmail_service,
            sender_mail,
            reply
        )
    else:
        print("email not sent")

    return reply

# ============================================================================
# Execute Workflow
# ============================================================================
print(get_result())



