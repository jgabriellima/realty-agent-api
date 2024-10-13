from abc import ABC, abstractmethod
from typing import Any


class QueueConsumer(ABC):
    @abstractmethod
    async def start_consuming(self):
        pass

    @abstractmethod
    async def stop_consuming(self):
        pass

    @abstractmethod
    async def close_connection(self):
        pass

    @abstractmethod
    async def process_message(self, message: Any):
        pass


class QueuePublisher(ABC):
    @abstractmethod
    async def publish_message(self, queue_name: str, message: Any):
        pass

    @abstractmethod
    async def close_connection(self):
        pass


class QueueHealthCheck(ABC):
    @abstractmethod
    async def check_health(self):
        pass


class DeadLetterQueueHandler(ABC):
    @abstractmethod
    async def process_dlq(self):
        pass

    @abstractmethod
    async def monitor_dlq(self):
        pass

    @abstractmethod
    async def requeue_message(self, message: Any):
        pass


class QueueConnectionManager(ABC):
    @abstractmethod
    async def get_connection(self):
        pass

    @abstractmethod
    async def close_connection(self):
        pass


class QueueMessageHandler(ABC):
    @abstractmethod
    async def ack(self, message):
        pass

    @abstractmethod
    async def nack(self, message, requeue=False):
        pass

    @abstractmethod
    async def retry(self, message, retries=0):
        pass


class QueueProcessor(ABC):
    @abstractmethod
    def process(self, ch, method, properties, body):
        pass

    @abstractmethod
    def retry_message(self, ch, method, retries: int = 5, backoff: int = 1):
        pass
