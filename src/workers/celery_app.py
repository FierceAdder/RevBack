"""Celery application instance and configuration for RevBack."""

import logging
from celery import Celery
from src.config import settings
from src.workers.beat_schedule import BEAT_SCHEDULE

logger = logging.getLogger("revback.celery")

celery_app = Celery(
    "revback",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max task duration
    beat_schedule=BEAT_SCHEDULE,
    broker_connection_retry_on_startup=True,
)

# Eagerly load tasks so they are registered on import
import src.workers.tasks  # noqa: E402

