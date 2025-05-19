# src/tournaments/tasks.py
from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from src.database import get_db, SessionLocal
from src.tournaments.models import Tournament
from src.tournaments.services import advance_tournament_stage
from src.logger import app_logger

# Создаем экземпляр Celery
celery_app = Celery('tournaments_tasks')

@celery_app.task
def check_and_advance_tournaments():
    """
    Задача для проверки и автоматического продвижения турниров на следующую стадию,
    если время текущей стадии истекло.
    """
    app_logger.info("Старт фоновой задачи: проверка и продвижение турниров")
    db = SessionLocal()
    try:
        # Получаем все активные турниры, у которых истекло время стадии
        tournaments = db.query(Tournament).filter(
            Tournament.current_stage != "completed",
            Tournament.stage_deadline < datetime.now(timezone.utc)
        ).all()
        
        for tournament in tournaments:
            try:
                advance_tournament_stage(db, tournament.tournament_id)
                app_logger.info(f"Турнир {tournament.tournament_id} автоматически переведен на следующую стадию")
            except Exception as e:
                # Логируем ошибку и продолжаем с другими турнирами
                app_logger.error(f"Ошибка при продвижении турнира {tournament.tournament_id}: {str(e)}")
    finally:
        db.close()
        app_logger.info("Фоновая задача завершена: проверка и продвижение турниров")

# Конфигурация Celery для задач по расписанию
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Проверяем и продвигаем турниры каждые 10 минут
    sender.add_periodic_task(600.0, check_and_advance_tournaments.s(), 
                             name='check tournaments every 10 minutes') 