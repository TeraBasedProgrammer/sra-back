import smtplib
from email.message import EmailMessage

from celery import Celery
from pydantic import EmailStr

from app.config.settings.base import settings

celery = Celery("tasks", broker=settings.REDIS_URL)


def get_email_template_dashboard(user_email: EmailStr, user_name: str, reset_link: str):
    email = EmailMessage()
    email["Subject"] = "Password reset request"
    email["From"] = settings.SMTP_USER
    email["To"] = user_email

    email.set_content(
        f"<div><p>Dear {user_name}</p>"
        "<p>You have requested a password reset for your account. To reset your password, please click on the following link:</p>"
        f"<p><a>{reset_link}</a></p>"
        "<p>If you did not request a password reset, please ignore this message.</p>"
        "<p>Best regards,</p>"
        "<p>Testeam</p></div>",
        subtype="html",
    )
    return email


@celery.task
def send_email_report_dashboard(user_email: EmailStr, user_name: str, reset_link: str):
    email = get_email_template_dashboard(user_email, user_name, reset_link)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(email)
