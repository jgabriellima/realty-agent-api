from unittest.mock import MagicMock, patch

import pytest

from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager
from api_template.queue.core.providers.rabbitmq.publisher import RabbitMQPublisher


@pytest.fixture
def queue_config():
    return {"broker_url": "localhost", "port": 5672, "ssl_context": None, "heartbeat": 600}


@pytest.fixture
def mock_channel():
    return MagicMock()


@pytest.fixture
def publisher(queue_config, mock_channel):
    with patch.object(RabbitMQConnectionManager, "channel", mock_channel):
        return RabbitMQPublisher("test_queue", queue_config)


def test_publish_message(publisher, mock_channel):
    publisher.publish_message("test_queue", "Test message")
    mock_channel.basic_publish.assert_called_once_with(
        exchange="", routing_key="test_queue", body="Test message", properties=MagicMock()
    )
