import logging
from typing import Any, Dict

from api_template.queue.config.queue_settings import QueueConfig, load_queue_settings
from api_template.queue.core.manager.interfaces import QueueHealthCheck
from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager

logger = logging.getLogger(__name__)


class RabbitMQHealthCheck(QueueHealthCheck):
    def __init__(self):
        self.queue_settings = load_queue_settings()

    async def check_health(self) -> Dict[str, Any]:
        overall_status = "healthy"
        queue_statuses = {}

        for queue_config in self.queue_settings.queues:
            if queue_config.type == "rabbitmq":
                status = await self._check_queue_health(queue_config)
                queue_statuses[queue_config.name] = status
                if status["status"] != "healthy":
                    overall_status = "unhealthy"

        return {"status": overall_status, "queues": queue_statuses}

    async def _check_queue_health(self, queue_config: QueueConfig) -> Dict[str, str]:
        try:
            connection_manager = RabbitMQConnectionManager(queue_config.name, queue_config)
            connection = await connection_manager.get_connection()

            if connection.is_open:
                await connection.close()
                return {"status": "healthy"}
            else:
                return {"status": "unhealthy", "error": "Connection is not open"}
        except Exception as e:
            logger.error(f"Error checking health for queue {queue_config.name}: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
