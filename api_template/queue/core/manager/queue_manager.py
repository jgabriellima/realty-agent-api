from typing import Dict

from api_template.queue.core.providers.rabbitmq.consumer import AsyncRabbitMQConsumer
from api_template.queue.core.providers.rabbitmq.publisher import AsyncRabbitMQPublisher


class QueueManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.publishers: Dict[str, AsyncRabbitMQPublisher] = {}
            self.consumers: Dict[str, AsyncRabbitMQConsumer] = {}
            self._initialized = True

    def register_publisher(self, queue_name: str, publisher: AsyncRabbitMQPublisher):
        self.publishers[queue_name] = publisher

    def get_publisher(self, queue_name: str) -> AsyncRabbitMQPublisher:
        publisher = self.publishers.get(queue_name)
        if not publisher:
            raise ValueError(f"Publisher for queue {queue_name} not found")
        return publisher

    def register_consumer(self, queue_name: str, consumer: AsyncRabbitMQConsumer):
        self.consumers[queue_name] = consumer

    def get_consumer(self, queue_name: str) -> AsyncRabbitMQConsumer:
        consumer = self.consumers.get(queue_name)
        if not consumer:
            raise ValueError(f"Consumer for queue {queue_name} not found")
        return consumer


# Singleton instance of QueueManager
queue_manager = QueueManager()
