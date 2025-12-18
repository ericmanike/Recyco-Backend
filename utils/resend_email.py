import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to_email: str, subject: str, html_body: str):
    try:
        response = resend.Emails.send({
            "from": os.getenv("MAIL_FROM"),  
            "to": to_email,
            "subject": subject,
            "html": html_body
        })

        return {
            "status": "success",
            "message": "Email sent successfully",
            "response": response
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
