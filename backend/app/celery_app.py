# app/celery_app.py
"""
Celery configuration.
Background jobs scheduler.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "finance_agent",
    broker=settings.REDIS_URL,      # Redis as message broker
    backend=settings.REDIS_URL,     # Redis as result backend
    include=[
        "app.tasks.categorisation",
        "app.tasks.forecasting",
        "app.tasks.anomaly_scan",
    ]
)

celery_app.conf.update(
    # Timezone
    timezone="Asia/Kolkata",
    enable_utc=True,

    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_acks_late=True,

    # Retry settings
    task_max_retries=3,
    task_default_retry_delay=60,  # 60 seconds

    # Scheduled tasks (Celery Beat)
    beat_schedule={
        # Nightly re-categorisation — 2 AM IST
        "nightly-recategorisation": {
            "task": "app.tasks.categorisation.recategorise_all_transactions",
            "schedule": crontab(hour=2, minute=0),
        },
        # Daily anomaly scan — 9 AM IST
        "daily-anomaly-scan": {
            "task": "app.tasks.anomaly_scan.scan_all_users",
            "schedule": crontab(hour=9, minute=0),
        },
        # Weekly forecast update — Sunday 1 AM IST
        "weekly-forecast-update": {
            "task": "app.tasks.forecasting.update_forecast_model",
            "schedule": crontab(hour=1, minute=0, day_of_week=0),
        },
    }
)