import functools
import time

from celery.utils.log import get_task_logger

from api_template.celery import celery_app

logger = get_task_logger(__name__)


def task_logging(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        task_name = func.__name__
        logger.info(f"Starting task: {task_name}")
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"Task {task_name} completed in {elapsed_time:.2f} seconds")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"Task {task_name} failed after {elapsed_time:.2f} seconds. Error: {str(e)}"
            )
            raise

    return wrapper


def retry_task(**kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                task = celery_app.tasks[func.__name__]
                raise task.retry(exc=exc, **kwargs)

        return wrapper

    return decorator


def set_timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task = celery_app.tasks[func.__name__]
            task.time_limit = seconds
            task.soft_time_limit = seconds - 5
            return func(*args, **kwargs)

        return wrapper

    return decorator
