from unittest.mock import MagicMock, patch

import pytest

from api_template.queue.core.providers.rabbitmq.manager import RabbitMQConnectionManager


@pytest.fixture
def queue_config():
    return {"broker_url": "localhost", "port": 5672, "ssl_context": None, "heartbeat": 600}


@patch("app.queue.providers.rabbitmq.manager.pika.BlockingConnection")
def test_connection_manager_initialization(mock_blocking_connection, queue_config):
    mock_blocking_connection.return_value = MagicMock()
    manager = RabbitMQConnectionManager("test_queue", queue_config)
    assert manager.connection is not None
    assert manager.channel is not None
    mock_blocking_connection.assert_called_once()


def test_close_connection():
    manager = MagicMock(RabbitMQConnectionManager)
    manager.close_connection()
    manager.connection.close.assert_called_once()
