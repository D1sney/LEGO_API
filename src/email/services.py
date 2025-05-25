import smtplib
from email.message import EmailMessage
from src.config import settings
from src.logger import app_logger

def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
        app_logger.info(f"Письмо успешно отправлено на {to_email} (subject: '{subject}')")
    except Exception as e:
        app_logger.error(f"Ошибка при отправке письма на {to_email}: {e}")
        raise 