from src.celery_app import celery_app
from src.email.services import send_email

@celery_app.task
def send_registration_email(to_email: str):
    subject = "Добро пожаловать в LEGO коллекцию!"
    body = "Спасибо за регистрацию в нашем сервисе LEGO!"
    send_email(to_email, subject, body) 