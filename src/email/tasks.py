from src.celery_app import celery_app
from src.email.services import send_email
from src.logger import app_logger

@celery_app.task
def send_registration_email(to_email: str):
    app_logger.info(f"Отправка приветственного письма на {to_email}")
    subject = "Добро пожаловать в LEGO коллекцию!"
    body = "Спасибо за регистрацию в нашем сервисе LEGO!"
    try:
        send_email(to_email, subject, body)
        app_logger.info(f"Приветственное письмо успешно отправлено на {to_email}")
    except Exception as e:
        app_logger.error(f"Ошибка при отправке приветственного письма на {to_email}: {e}")
        raise

@celery_app.task
def send_verification_code_email(to_email: str, verification_code: str):
    """Фоновая задача для отправки кода подтверждения email"""
    app_logger.info(f"Отправка кода подтверждения на {to_email}")
    subject = "Код подтверждения LEGO API"
    body = f"Ваш код подтверждения: {verification_code}"
    try:
        send_email(to_email, subject, body)
        app_logger.info(f"Код подтверждения успешно отправлен на {to_email}")
    except Exception as e:
        app_logger.error(f"Ошибка при отправке кода подтверждения на {to_email}: {e}")
        raise 