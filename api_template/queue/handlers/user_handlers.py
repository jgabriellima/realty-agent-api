import logging

from api_template.api.v1.dependencies import get_db
from api_template.api.v1.services.user_service import UserService

logger = logging.getLogger(__name__)


class UserHandler:
    def __init__(self):
        self.user_service = UserService(get_db())

    def send_audio(self, message):
        self.user_service.notify_user(message["user_id"], "audio", message["content"])
        print(f"Sending audio message: {message}")

    def test_message(self, message):
        print(f"Received test message: {message}")
