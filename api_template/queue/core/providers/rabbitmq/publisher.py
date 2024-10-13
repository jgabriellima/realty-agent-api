import json
from typing import Any, Dict, Union

import aio_pika

from api_template.queue.core.manager.circuit_breaker import QueueCircuitBreaker
from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager


class AsyncRabbitMQPublisher:
    def __init__(self, queue_name, queue_config):
        self.queue_name = queue_name
        self.connection_manager = RabbitMQConnectionManager(queue_name, queue_config)
        self.circuit_breaker = QueueCircuitBreaker()

    async def publish_message(self, queue_name: str, message: Union[str, Dict[str, Any]]):
        await self.circuit_breaker.execute(self._publish, queue_name, message)

    async def _publish(self, queue_name: str, message: Union[str, Dict[str, Any]]):
        connection = await self.connection_manager.get_async_connection()
        async with connection:
            channel = await connection.channel(publisher_confirms=True)
            await channel.declare_queue(queue_name, durable=True)

            if isinstance(message, dict):
                message = json.dumps(message)

            if not isinstance(message, str):
                message = str(message)

            print(f"Publishing message: {message} : {queue_name}")
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()), routing_key=queue_name
            )
            print("Message published")

        await self.connection_manager.release_async_connection(connection)

    async def close_all(self):
        await self.connection_manager.close_all_connections()

    async def close_connection(self):
        await self.connection_manager.close_all_connections()
