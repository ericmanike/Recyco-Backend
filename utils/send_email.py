from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER= "smtp.gmail.com", 
    MAIL_STARTTLS=True,    
    MAIL_SSL_TLS=False,    
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

print("Email configuration loaded:", conf)

class EmailSchema(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str
    subtype: Optional[MessageType] = MessageType.html  # html or plain text


async def send_email(email: EmailSchema):
    """
    Utility to send email using FastAPI-Mail.
    Accepts EmailSchema object.
    """

    message = MessageSchema(
        subject=email.subject,
        recipients=email.recipients,
        body=email.body,
        subtype=email.subtype,
    )

    fm = FastMail(conf)

    try:
        await fm.send_message(message)
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
