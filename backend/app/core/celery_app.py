from celery import Celery
from app.config import settings

celery_app = Celery(
    "ecom",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Auto-close expired banners every hour
        "deactivate-expired-banners": {
            "task": "app.tasks.email_tasks.deactivate_expired_banners",
            "schedule": 3600.0,
        },
    },
)
