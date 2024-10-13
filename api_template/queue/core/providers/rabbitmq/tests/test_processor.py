from unittest.mock import MagicMock

import pytest

from api_template.queue.core.providers.rabbitmq.processor import RabbitMQProcessor


@pytest.fixture
def processor():
    return RabbitMQProcessor()


def test_process_message_success(processor):
    mock_channel = MagicMock()
    processor.process(mock_channel, MagicMock(), MagicMock(), b"Test message")
    mock_channel.basic_ack.assert_called_once()


def test_process_message_failure(processor):
    mock_channel = MagicMock()
    processor.process = MagicMock(side_effect=Exception("Processing error"))
    with pytest.raises(Exception):
        processor.process(mock_channel, MagicMock(), MagicMock(), b"Test message")
    mock_channel.basic_nack.assert_called()
