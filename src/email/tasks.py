from src.celery_app import celery_app
from src.email.services import send_email

@celery_app.task
def send_registration_email(to_email: str):
    subject = "Добро пожаловать в LEGO коллекцию!"
    body = "Спасибо за регистрацию в нашем сервисе LEGO!"
    send_email(to_email, subject, body)

@celery_app.task
def send_verification_code_email(to_email: str, verification_code: str):
    """Фоновая задача для отправки кода подтверждения email"""
    subject = "Код подтверждения LEGO API"
    body = f"Ваш код подтверждения: {verification_code}"
    send_email(to_email, subject, body) 