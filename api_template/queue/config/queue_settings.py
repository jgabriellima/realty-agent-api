import logging
import os
import ssl
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel

from api_template.config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class QueueConfig(BaseModel):
    name: str
    type: str
    port: int
    heartbeat: int
    broker_url: Optional[str] = None
    enable_publisher: bool = True
    enable_consumer: bool = True
    options: Optional[dict] = None
    ssl_context: Optional[Any] = None
    heartbeat: int = 60
    enable_dlq: bool = False

    def create_ssl_context(self, ssl_options: dict) -> Optional[ssl.SSLContext]:
        if not ssl_options.get("enabled"):
            return None

        context = ssl.create_default_context(cafile=ssl_options.get("ca_certs"))
        context.load_cert_chain(
            certfile=ssl_options.get("certfile"), keyfile=ssl_options.get("keyfile")
        )
        return context

    @property
    def username(self):
        return settings.QUEUE_USERNAME

    @property
    def password(self):
        return settings.QUEUE_PASSWORD


class QueueSettings(BaseModel):
    queues: List[QueueConfig] = []


def load_queue_settings() -> QueueSettings:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "queues.yaml")

    if not os.path.exists(file_path):
        logger.info(f"Configuration file {file_path} not found. No queues will be configured.")
        return QueueSettings()

    with open(file_path, "r") as f:
        config_data = yaml.safe_load(f)
        if not config_data:
            logger.info(f"Configuration file {file_path} is empty. No queues will be configured.")
            return QueueSettings()

    logger.info(f"Loaded queue configuration from {file_path} :: {config_data}")
    return QueueSettings(**config_data)
