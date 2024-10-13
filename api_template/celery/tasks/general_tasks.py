from api_template.celery.app import celery_app
from api_template.celery.core.base import BaseTask
from api_template.celery.core.decorators import retry_task, set_timeout


@celery_app.task(bind=True, base=BaseTask)
@retry_task(max_retries=3, countdown=60)
def example_task(self, param):
    try:
        result = f"Task completed with param: {param}"
        return result
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=BaseTask,
    max_retries=10,
    retry_backoff=True,
    retry_backoff_max=3600,  # 1 hour
    rate_limit="5/m",
)
@set_timeout(1800)  # 30 minutes
def complex_task(self, param):
    try:
        result = f"Complex task completed with param: {param}"
        return result
    except Exception as e:
        self.retry(exc=e)
