from celery.exceptions import Retry

from api_template.celery.app import celery_app
from api_template.celery.core.base import BaseTask


class UserTaskException(Exception):
    pass


@celery_app.task(bind=True, base=BaseTask)
class CreateUserTask(BaseTask):
    name = "create_user_task"

    def run(self, username, email):
        try:
            result = f"User created: {username} ({email})"
            self.on_success(result)
            return result
        except Exception as e:
            self.on_failure(e)
            raise UserTaskException(f"Failed to create user: {str(e)}")


@celery_app.task(bind=True, base=BaseTask)
class UpdateUserProfileTask(BaseTask):
    name = "update_user_profile_task"
    max_retries = 3
    rate_limit = "5/m"
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes

    def run(self, user_id, profile_data):
        try:
            result = f"Profile updated for user {user_id}"
            self.on_success(result)
            return result
        except Exception as e:
            self.on_retry(e)
            raise Retry(exc=e)
