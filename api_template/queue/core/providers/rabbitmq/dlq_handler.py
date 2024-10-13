import asyncio
import logging

from api_template.queue.core.manager.interfaces import DeadLetterQueueHandler
from api_template.queue.core.providers.rabbitmq.publisher import AsyncRabbitMQPublisher

logger = logging.getLogger(__name__)


class RabbitMQDeadLetterQueueHandler(DeadLetterQueueHandler):
    def __init__(self, dlq_name: str, main_queue_name: str, publisher: AsyncRabbitMQPublisher):
        self.dlq_name = dlq_name
        self.main_queue_name = main_queue_name
        self.publisher = publisher
        self.connection_manager = (
            publisher.connection_manager
        )  # Reusing the publisher's connection manager

    async def process_dlq(self):
        """Process all messages from the Dead Letter Queue (DLQ)"""
        while True:
            try:
                connection = await self.connection_manager.get_async_connection()
                async with connection:
                    channel = await connection.channel()
                    queue = await channel.declare_queue(self.dlq_name, durable=True)

                    async with queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            if not message:
                                break
                            async with message.process():
                                await self.requeue_message(message)
            except asyncio.CancelledError:
                logger.info("Cancelled DLQ processing")
                break
            except Exception as e:
                logger.error(f"Error processing DLQ: {str(e)}")
                await asyncio.sleep(5)  # Wait before trying to reconnect

    async def monitor_dlq(self):
        """Monitor the Dead Letter Queue and process it if there are messages"""
        while True:
            try:
                connection = await self.connection_manager.get_async_connection()
                async with connection:
                    channel = await connection.channel()
                    queue = await channel.declare_queue(self.dlq_name, durable=True)
                    message_count = queue.declaration_result.message_count
                    logger.info(f"DLQ {self.dlq_name} message count: {message_count}")
                    if message_count > 0:
                        await self.process_dlq()
            except asyncio.CancelledError:
                logger.info("Cancelled DLQ monitoring")
                break
            except Exception as e:
                logger.error(f"Error monitoring DLQ: {str(e)}")
                await asyncio.sleep(5)  # Wait before trying to reconnect
            await asyncio.sleep(60)  # Check every minute

    async def requeue_message(self, message):
        """Reprocess the message from the DLQ and send it to the main queue"""
        try:
            # Process the message (implement your logic here)
            logger.info(f"Processing message from DLQ: {message.body.decode()}")
            # If successful, republish to the main queue
            await self.publisher.publish_message(self.main_queue_name, message.body.decode())
        except Exception as e:
            logger.error(f"Error requeueing DLQ message: {e}")
            await message.nack(requeue=True)
