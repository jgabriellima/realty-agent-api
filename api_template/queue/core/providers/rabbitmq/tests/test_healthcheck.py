from unittest.mock import patch

from api_template.queue.core.providers.rabbitmq.healthcheck import RabbitMQHealthCheck


@patch("app.queue.providers.rabbitmq.healthcheck.RabbitMQConnectionManager")
def test_health_check_healthy(mock_manager):
    mock_manager.return_value.connection.is_open = True
    health_checker = RabbitMQHealthCheck()
    health_status = health_checker.check_health()
    assert health_status["status"] == "healthy"


@patch("app.queue.providers.rabbitmq.healthcheck.RabbitMQConnectionManager")
def test_health_check_unhealthy(mock_manager):
    mock_manager.return_value.connection.is_open = False
    health_checker = RabbitMQHealthCheck()
    health_status = health_checker.check_health()
    assert health_status["status"] == "unhealthy"
