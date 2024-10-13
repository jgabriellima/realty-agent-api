import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager

import psutil
from fastapi import FastAPI

from api_template.queue.config.queue_settings import load_queue_settings
from api_template.queue.config.queue_types import QueueType
from api_template.queue.core.manager.message_processor import MessageProcessor
from api_template.queue.core.manager.queue_manager import queue_manager
from api_template.queue.core.providers.rabbitmq.consumer import AsyncRabbitMQConsumer
from api_template.queue.core.providers.rabbitmq.dlq_handler import RabbitMQDeadLetterQueueHandler
from api_template.queue.core.providers.rabbitmq.publisher import AsyncRabbitMQPublisher
from api_template.queue.handlers.register_handlers import register_user_handlers
from api_template.utils.logging import log_message

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    """
    Lifespan handler for FastAPI app
    :param app:
    :return:
    """
    logger.info("Starting lifespan_handler...")
    app.state.executor = ProcessPoolExecutor()
    consumers_publishers = setup_queue()

    yield

    logger.info("Shutting down lifespan_handler...")
    for consumer, publisher in consumers_publishers:
        if consumer:
            await consumer.close_connection()
        if publisher:
            await publisher.close_connection()

    app.state.executor.shutdown()


def setup_parallel_consumers(queue_config, consumer, num_consumers=5):
    """
    Setup parallel consumers
    :param queue_config:
    :param consumer:
    :param num_consumers:
    :return:
    """
    with ThreadPoolExecutor(max_workers=num_consumers) as executor:
        futures = [executor.submit(consumer.start_consuming) for _ in range(num_consumers)]
        for future in as_completed(futures):
            try:
                future.result()
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                logger.info(f"Resource usage: CPU {cpu_usage}%, Memory {memory_usage}%")
            except Exception as e:
                log_message("consumer_error", queue_config.name, error=str(e))


def get_processor(queue_type: QueueType):
    """
    Get message processor based on queue type
    :param queue_type:
    :return:
    """
    if queue_type == QueueType.RABBITMQ:
        from api_template.queue.core.providers.rabbitmq.processor import RabbitMQProcessor

        return RabbitMQProcessor()
    else:
        raise ValueError(f"Unsupported queue type: {queue_type.value}")


def get_consumer(queue_type: QueueType, queue_name: str, callback, queue_config):
    """
    Get consumer based on queue type
    :param queue_type:
    :param queue_name:
    :param callback:
    :param queue_config:
    :return:
    """
    if queue_type == QueueType.RABBITMQ:
        from api_template.queue.core.providers.rabbitmq.consumer import AsyncRabbitMQConsumer

        return AsyncRabbitMQConsumer(queue_name, callback, queue_config)

    else:
        raise ValueError(f"Unsupported queue type: {queue_type.value}")


def get_publisher(queue_type: QueueType, queue_name: str, queue_config):
    """
    Get publisher based on queue type
    :param queue_type:
    :param queue_name:
    :param queue_config:
    :return:
    """
    if queue_type == QueueType.RABBITMQ:
        from api_template.queue.core.providers.rabbitmq.publisher import AsyncRabbitMQPublisher

        return AsyncRabbitMQPublisher(queue_name, queue_config)
    else:
        raise ValueError(f"Unsupported queue type: {queue_type.value}")


def setup_channel(queue_config):
    """
    Setup channel for queue
    :param queue_config:
    :return:
    """
    processor = get_processor(QueueType(queue_config.type))
    consumer = None
    publisher = None

    if queue_config.enable_consumer:
        consumer = get_consumer(
            QueueType(queue_config.type), queue_config.name, processor.process, queue_config
        )
        setup_parallel_consumers(queue_config, consumer, num_consumers=3)

    if queue_config.enable_publisher:
        publisher = get_publisher(QueueType(queue_config.type), queue_config.name, queue_config)
        log_message("publisher_ready", queue_config.name)

    return consumer, publisher


def setup_queue():
    """
    Setup queue and register them to the QueueManager
    :param app:
    :return:
    """
    settings = load_queue_settings()
    consumers_publishers = []

    # Setup message processor and register handlers
    message_processor = MessageProcessor()

    register_user_handlers(message_processor)

    for queue_config in settings.queues:
        if queue_config.type == QueueType.RABBITMQ.value:
            try:
                logger.info(f"Setting up RabbitMQ queue: {queue_config.name}")

                consumer = (
                    AsyncRabbitMQConsumer(queue_config.name, queue_config, message_processor)
                    if queue_config.enable_consumer
                    else None
                )
                publisher = (
                    AsyncRabbitMQPublisher(queue_config.name, queue_config)
                    if queue_config.enable_publisher
                    else None
                )

                if consumer:
                    asyncio.create_task(consumer.start_consuming())
                    queue_manager.register_consumer(queue_config.name, consumer)

                if publisher and queue_config.enable_dlq:
                    dlq_handler = RabbitMQDeadLetterQueueHandler(
                        f"{queue_config.name}_dlq", queue_config.name, publisher
                    )
                    asyncio.create_task(dlq_handler.monitor_dlq())

                if publisher:
                    queue_manager.register_publisher(queue_config.name, publisher)
                    logger.info(f"Publisher for {queue_config.name} is ready.")

                consumers_publishers.append((consumer, publisher))
            except Exception as e:
                logger.error(f"Error setting up queue {queue_config.name}: {e}")

    return consumers_publishers
