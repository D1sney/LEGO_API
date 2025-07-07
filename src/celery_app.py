# src/celery_app.py
from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    'lego_collection',
    # Формируем URL брокера из настроек окружения
    broker=f"pyamqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    backend='rpc://',
    include=[
        'src.tournaments.tasks',
        'src.email.tasks',
    ]
)

celery_app.conf.update(
    enable_utc=True,
    timezone='UTC',
    beat_schedule={
        'check-tournaments-every-10-minutes': {
            'task': 'src.tournaments.tasks.check_and_advance_tournaments',
            'schedule': crontab(), # Это означает 1 минута, можно просто написать 60.0
        },
    }
) 