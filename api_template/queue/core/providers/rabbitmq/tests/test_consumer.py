from unittest.mock import MagicMock, patch

import pytest

from api_template.queue.core.providers.rabbitmq.consumer import RabbitMQConsumer
from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager


@pytest.fixture
def queue_config():
    return {"broker_url": "localhost", "port": 5672, "ssl_context": None, "heartbeat": 600}


@pytest.fixture
def mock_channel():
    return MagicMock()


@pytest.fixture
def consumer(queue_config, mock_channel):
    with patch.object(RabbitMQConnectionManager, "channel", mock_channel):
        return RabbitMQConsumer("test_queue", MagicMock(), queue_config)


def test_start_consuming(consumer, mock_channel):
    consumer.start_consuming()
    mock_channel.basic_consume.assert_called_with(
        queue="test_queue", on_message_callback=consumer.callback, auto_ack=False
    )


def test_close_connection(consumer, mock_channel):
    consumer.close_connection()
    mock_channel.connection.close.assert_called_once()
