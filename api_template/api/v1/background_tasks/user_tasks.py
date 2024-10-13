from fastapi import BackgroundTasks

from api_template.api.v1.services.user_service import UserService


def send_welcome_email(
    background_tasks: BackgroundTasks, user_email: str, user_service: UserService
):
    background_tasks.add_task(user_service.send_email, user_email)
