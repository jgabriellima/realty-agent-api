import asyncio

from api_template.queue.config.queue_settings import QueueConfig
from api_template.queue.core.providers.rabbitmq.publisher import AsyncRabbitMQPublisher


async def main():
    user_channel = "user_channel"
    queue_config = QueueConfig(
        name=user_channel,
        type="rabbitmq",
        port=5672,
        broker_url="localhost",
        enable_publisher=True,
        enable_consumer=True,
        options=None,
        ssl_context=None,
        heartbeat=60,
    )

    publisher = AsyncRabbitMQPublisher(user_channel, queue_config)
    await publisher.publish_message(user_channel, "test message")
    # await publisher.close_all()


if __name__ == "__main__":
    asyncio.run(main())
