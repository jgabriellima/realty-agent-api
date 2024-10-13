from api_template.queue.core.manager.message_processor import MessageProcessor
from api_template.queue.handlers.user_handlers import UserHandler


def register_user_handlers(processor: MessageProcessor):
    # User handler
    user_handler = UserHandler()
    processor.add_handler("send_audio", user_handler.send_audio)
    processor.add_handler("test_message", user_handler.test_message)
