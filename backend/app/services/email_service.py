import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.office365.com"
_SMTP_PORT = 587


def send_email(summary: str, contact_info: Optional[dict] = None) -> bool:
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("EMAIL_TO")

    if not all([sender, password, recipient]):
        logger.error("Email config incomplete — check EMAIL_USER, EMAIL_PASS, EMAIL_TO")
        return False

    contact_block = ""
    if contact_info:
        contact_block = (
            "Customer Contact Details\n"
            "─────────────────────────\n"
            f"Business : {contact_info.get('business_name', 'N/A')}\n"
            f"Email    : {contact_info.get('email', 'N/A')}\n"
            f"Phone    : {contact_info.get('phone', 'N/A')}\n\n"
        )

    body = f"{contact_block}Issue Summary\n─────────────────────────\n{summary}"

    msg = MIMEText(body)
    msg["Subject"] = "New Customer Support Request"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        logger.info("Support email sent to %s", recipient)
        return True
    except smtplib.SMTPException as e:
        logger.error("Failed to send email: %s", e)
        return False
