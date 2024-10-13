import asyncio
import json
import logging
import traceback

from api_template.queue.core.manager.interfaces import QueueConsumer
from api_template.queue.core.manager.message_processor import MessageProcessor
from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager
from api_template.queue.core.providers.rabbitmq.message_handler import RabbitMQMessageHandler

logger = logging.getLogger(__name__)


class AsyncRabbitMQConsumer(QueueConsumer):
    def __init__(self, queue_name, queue_config, message_processor: MessageProcessor):
        self.queue_name = queue_name
        self.connection_manager = RabbitMQConnectionManager(queue_name, queue_config)
        self.message_processor = message_processor
        self._running = False
        self._connection = None
        self._channel = None

    async def process_message(self, message):
        # try:
        logger.info(f"Processing message: {message}")
        message_body = json.loads(message.body.decode())
        message_type = message_body.get("type")
        if message_type:
            queue_handler = RabbitMQMessageHandler(self._channel, message)
            logger.info(
                f"Processing message: {message_type} - Body: {message_body} - Handler: {queue_handler} - Method: {message}"
            )
            logger.info(f"message_processor: {self.message_processor}")
            await self.message_processor.process(message_type, message_body, queue_handler)
        else:
            raise ValueError("Message type not specified")
        # except json.JSONDecodeError:
        #     logger.error("Failed to decode message JSON")
        # except Exception as e:
        #     raise e
        #     logger.error(f"Error processing message: {str(e)}")

    async def start_consuming(self):
        self._running = True
        while self._running:
            try:
                self._connection = await self.connection_manager.get_async_connection()
                self._channel = await self._connection.channel()
                queue = await self._channel.declare_queue(self.queue_name, durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        if not self._running:
                            break
                        async with message.process():
                            await self.process_message(message)
            except asyncio.CancelledError:
                logger.info("Consumer cancelled")
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {str(e)} :: {traceback.format_exc()}")
                await asyncio.sleep(5)
            finally:
                if self._channel and not self._channel.is_closed:
                    await self._channel.close()
                if self._connection and not self._connection.is_closed:
                    await self.connection_manager.release_async_connection(self._connection)
                    self._connection = None
                    self._channel = None

    async def stop_consuming(self):
        self._running = False
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def close_connection(self):
        await self.stop_consuming()
