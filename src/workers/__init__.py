"""Celery workers package for RevBack asynchronous scheduling and background jobs."""

from src.workers.celery_app import celery_app

__all__ = ["celery_app"]
