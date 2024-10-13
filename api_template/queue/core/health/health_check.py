from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from api_template.queue.config.queue_settings import load_queue_settings
from api_template.queue.config.queue_types import QueueType
from api_template.queue.core.manager.interfaces import QueueHealthCheck

router = APIRouter()


def get_health_checker(queue_type: QueueType) -> QueueHealthCheck:
    if queue_type == QueueType.RABBITMQ:
        from api_template.queue.core.providers.rabbitmq.healthcheck import RabbitMQHealthCheck

        return RabbitMQHealthCheck()
    # Add more queue types as needed
    else:
        raise ValueError(f"Unsupported queue type: {queue_type}")


@router.get("/health/queue")
async def health_check() -> Dict[str, Any]:
    settings = load_queue_settings()
    overall_status = "healthy"
    queue_statuses = {}

    for queue_config in settings.queues:
        try:
            health_checker = get_health_checker(QueueType(queue_config.type))
            health_status = await health_checker.check_health()
            queue_statuses[queue_config.name] = health_status
            if health_status["status"] != "healthy":
                overall_status = "unhealthy"
        except Exception as e:
            queue_statuses[queue_config.name] = {"status": "error", "message": str(e)}
            overall_status = "unhealthy"

    result = {"status": overall_status, "queues": queue_statuses}

    if overall_status != "healthy":
        raise HTTPException(status_code=503, detail=result)

    return result
