from celery import Celery

from api_template.celery.config.celery_config import CeleryConfig

mapped_tasks = ["api_template.celery.tasks.general_tasks", "api_template.celery.tasks.user_tasks"]


def create_celery_app():
    app = Celery("api_template", include=mapped_tasks)
    app.config_from_object(CeleryConfig())
    app.conf.update(
        worker_send_task_events=True,
        task_send_sent_event=True,
    )
    app.autodiscover_tasks(["api_template.celery.tasks"], force=True)

    # Log the registered tasks
    registered_tasks = app.tasks.keys()
    print(f"Registered tasks: {registered_tasks}")

    return app


celery_app = create_celery_app()

if __name__ == "__main__":
    celery_app.start()
