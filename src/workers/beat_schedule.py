"""Celery Beat cron schedule configuration for RevBack."""

from celery.schedules import crontab

BEAT_SCHEDULE = {
    # Every 1 hour — evaluate debtor commitments against current timestamp
    "check-promise-deadlines-every-hour": {
        "task": "src.workers.tasks.check_promise_deadlines",
        "schedule": crontab(minute=0),
    },
    # Every 6 hours — identify dormant/stale receivables needing intervention
    "process-stale-receivables-every-6-hours": {
        "task": "src.workers.tasks.process_stale_receivables",
        "schedule": crontab(minute=30, hour="*/6"),
    },
    # Daily at midnight IST (18:30 UTC / 00:00 IST) — capture daily recovery metrics snapshot
    "daily-recovery-snapshot": {
        "task": "src.workers.tasks.daily_metrics_snapshot",
        "schedule": crontab(minute=0, hour=0),
    },
    # Weekly on Monday at 02:00 IST — audit all promise statuses
    "weekly-promise-audit": {
        "task": "src.workers.tasks.weekly_promise_audit",
        "schedule": crontab(minute=0, hour=2, day_of_week=1),
    },
}
