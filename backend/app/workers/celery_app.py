from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("shangtugongfang", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_default_queue = "q_default"


@celery_app.task(name="jobs.run_job_item")
def run_job_item(job_item_id: str) -> dict:
    return {"job_item_id": job_item_id, "status": "queued"}
