import logging
from typing import Any, Callable, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from api_template.queue.core.manager.queue_message_handler import QueueMessageHandler

logger = logging.getLogger(__name__)


class MessageProcessor:
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    def add_handler(self, message_type: str, handler: Callable):
        self.handlers[message_type] = handler

    async def process(self, message_type: str, message: Any, queue_handler: "QueueMessageHandler"):
        logger.info(
            f"Processing message: {message_type} - Body: {message} - Handler: {queue_handler}"
        )
        handler = self.handlers.get(message_type)
        if handler:
            try:
                handler(message)
                await queue_handler.ack()
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await queue_handler.retry(message)
        else:
            logger.error(f"No handler registered for message type: {message_type}")
            await queue_handler.nack(message)
