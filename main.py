from dotenv import load_dotenv
load_dotenv()
from features.retrivier.main import get_query, fetch_gmail, gmail_service
from features.sendmail.send import send_mail






def get_result():
    result = fetch_gmail(gmail_service)

    if not result:
        return f"there is no mail"
    
    text, sender_mail = result
    
    print(f"email:{text}")
    print(f"send mail:{sender_mail}")

    reply = get_query(text)
    print(f"\n\n Gnerated reply:")
    print(reply)

    

    choose = input("\n Should send  this mail ? (yes/no): ").strip().lower()
    if choose in ["yes", "y"]:


        send_mail(
            gmail_service,
            sender_mail,
            reply
        )

    else:
        print("email not sent")

    return reply

print(get_result())



