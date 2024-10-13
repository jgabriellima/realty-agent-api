from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from api_template.queue.config.queue_types import QueueType
from api_template.queue.setup import setup_queue


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def mock_user_service():
    return MagicMock()


@pytest.mark.asyncio
@patch("app.queue.setup.load_queue_settings")
@patch("app.queue.setup.AsyncRabbitMQConsumer")
@patch("app.queue.setup.AsyncRabbitMQPublisher")
@patch("app.queue.setup.RabbitMQDeadLetterQueueHandler")
@patch("app.queue.setup.MessageProcessor")
async def test_setup_queue_no_config(
    mock_message_processor,
    mock_dlq_handler,
    mock_publisher,
    mock_consumer,
    mock_load_queue_settings,
    app,
    mock_user_service,
):
    mock_load_queue_settings.return_value = MagicMock(queues=[])
    consumers_publishers = await setup_queue()
    assert len(consumers_publishers) == 0
    mock_consumer.assert_not_called()
    mock_publisher.assert_not_called()


@pytest.mark.asyncio
@patch("app.queue.setup.load_queue_settings")
@patch("app.queue.setup.AsyncRabbitMQConsumer")
@patch("app.queue.setup.AsyncRabbitMQPublisher")
@patch("app.queue.setup.RabbitMQDeadLetterQueueHandler")
@patch("app.queue.setup.MessageProcessor")
@patch("app.queue.setup.register_handlers")
async def test_setup_queue_with_config(
    mock_register_handlers,
    mock_message_processor,
    mock_dlq_handler,
    mock_publisher,
    mock_consumer,
    mock_load_queue_settings,
    app,
    mock_user_service,
):
    mock_queue_config = MagicMock(
        name="test_queue",
        type=QueueType.RABBITMQ,
        enable_consumer=True,
        enable_publisher=True,
        enable_dlq=True,
    )
    mock_load_queue_settings.return_value = MagicMock(queues=[mock_queue_config])

    mock_consumer_instance = AsyncMock()
    mock_consumer.return_value = mock_consumer_instance

    mock_publisher_instance = AsyncMock()
    mock_publisher.return_value = mock_publisher_instance

    mock_dlq_handler_instance = AsyncMock()
    mock_dlq_handler.return_value = mock_dlq_handler_instance

    consumers_publishers = await setup_queue()

    assert len(consumers_publishers) == 1
    consumer, publisher = consumers_publishers[0]

    assert consumer == mock_consumer_instance
    assert publisher == mock_publisher_instance

    mock_consumer.assert_called_once_with(
        mock_queue_config.name, mock_queue_config, mock_message_processor.return_value
    )
    mock_publisher.assert_called_once_with(mock_queue_config.name, mock_queue_config)
    mock_dlq_handler.assert_called_once_with(
        f"{mock_queue_config.name}_dlq", mock_queue_config.name, mock_publisher_instance
    )

    mock_consumer_instance.start_consuming.assert_called_once()
    mock_dlq_handler_instance.monitor_dlq.assert_called_once()
    mock_register_handlers.assert_called_once()


@pytest.mark.asyncio
@patch("app.queue.setup.load_queue_settings")
@patch("app.queue.setup.AsyncRabbitMQConsumer")
@patch("app.queue.setup.AsyncRabbitMQPublisher")
@patch("app.queue.setup.RabbitMQDeadLetterQueueHandler")
@patch("app.queue.setup.MessageProcessor")
async def test_setup_queue_consumer_only(
    mock_message_processor,
    mock_dlq_handler,
    mock_publisher,
    mock_consumer,
    mock_load_queue_settings,
    app,
    mock_user_service,
):
    mock_queue_config = MagicMock(
        name="test_queue",
        type=QueueType.RABBITMQ,
        enable_consumer=True,
        enable_publisher=False,
        enable_dlq=False,
    )
    mock_load_queue_settings.return_value = MagicMock(queues=[mock_queue_config])

    mock_consumer_instance = AsyncMock()
    mock_consumer.return_value = mock_consumer_instance

    consumers_publishers = await setup_queue()

    assert len(consumers_publishers) == 1
    consumer, publisher = consumers_publishers[0]

    assert consumer == mock_consumer_instance
    assert publisher is None

    mock_consumer.assert_called_once_with(
        mock_queue_config.name, mock_queue_config, mock_message_processor.return_value
    )
    mock_publisher.assert_not_called()
    mock_dlq_handler.assert_not_called()

    mock_consumer_instance.start_consuming.assert_called_once()
