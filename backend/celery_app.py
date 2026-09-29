"""
Celery Application and Task Queue Configuration.
Brokers heavy raster math and model inference via Redis.
"""

from celery import Celery
from backend.config import settings

celery_app = Celery(
    "landslide_tasks",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=120, # 2 minute timeout per heavy raster job
    broker_connection_retry_on_startup=False,
    broker_connection_timeout=0.5,
    broker_transport_options={
        "max_retries": 0,
        "socket_timeout": 0.5,
        "socket_connect_timeout": 0.5,
    },
)
