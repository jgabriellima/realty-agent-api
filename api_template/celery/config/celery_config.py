from api_template.celery.config.celery_settings import celery_settings


class CeleryConfig:
    broker_url = celery_settings.CELERY_BROKER_URL
    result_backend = celery_settings.CELERY_RESULT_BACKEND

    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    timezone = "UTC"
    enable_utc = True

    task_routes = {
        "api_template.celery.tasks.user_tasks.*": {"queue": "user_tasks"},
        "api_template.celery.tasks.general_tasks.*": {"queue": "general_tasks"},
    }

    task_default_queue = "default"
    task_queues = {"default": {}, "user_tasks": {}, "general_tasks": {}}

    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 1000
    worker_max_memory_per_child = 200000  # 200MB

    task_track_started = True
    task_time_limit = 3600  # 1 hour
    task_soft_time_limit = 3300  # 55 minutes
    task_acks_late = True
    task_reject_on_worker_lost = True
    worker_concurrency = 4
