"""SMTP email delivery service."""
import os
import smtplib
from email.message import EmailMessage

from flask import current_app


def send_verification_email(recipient, code):
    server_name = os.getenv("MAIL_SERVER")
    username = os.getenv("MAIL_USERNAME")
    # Google displays App Passwords with spaces; SMTP authentication expects
    # the same 16 characters without those display spaces.
    password = (os.getenv("MAIL_PASSWORD") or "").replace(" ", "")
    sender = os.getenv("MAIL_DEFAULT_SENDER") or username
    if not all([server_name, username, password, sender]):
        current_app.logger.warning("OTP email not sent: MAIL_* settings are incomplete.")
        return False
    message = EmailMessage()
    message["Subject"] = "Verify your Infanta, I Hopping account"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(f"Your six-digit verification code is {code}. It expires in five minutes.")
    try:
        with smtplib.SMTP(server_name, int(os.getenv("MAIL_PORT", "587")), timeout=15) as smtp:
            if os.getenv("MAIL_USE_TLS", "true").lower() == "true":
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError, ValueError):
        # Keep credentials out of the terminal while preserving the useful traceback.
        current_app.logger.exception("OTP email delivery failed.")
        return False

    return True

