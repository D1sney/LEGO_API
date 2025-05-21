# src/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'lego_collection',
    broker='pyamqp://guest@localhost//',  # Можно заменить на redis://... если используешь Redis
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