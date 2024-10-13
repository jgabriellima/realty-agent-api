import logging
import time

from api_template.queue.core.manager.interfaces import QueueProcessor
from api_template.utils.logging import log_message

logger = logging.getLogger(__name__)


class RabbitMQProcessor(QueueProcessor):
    def process(self, ch, method, properties, body):
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log_message("message_processed", "queue_name_here", message=body.decode())
        except Exception as e:
            log_message("processing_error", "queue_name_here", message=body.decode(), error=str(e))
            self.retry_message(ch, method)

    def retry_message(self, ch, method, retries: int = 5, backoff: int = 1):
        if retries > 0:
            time.sleep(backoff)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            log_message(
                "message_retry",
                "queue_name_here",
                error=f"Retrying message with backoff {backoff}. Retries left: {retries - 1}",
            )
            self.retry_message(ch, method, retries=retries - 1, backoff=backoff * 2)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            log_message(
                "message_dlq",
                "queue_name_here",
                error="Message moved to Dead Letter Queue after max retries.",
            )
