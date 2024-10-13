import logging
import os
from typing import Optional

import yaml
from celery.schedules import crontab
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from api_template.queue.config.queue_types import QueueType

# Setup logging
logger = logging.getLogger(__name__)


class CelerySettings(BaseSettings):
    # Integrating Celery settings
    CELERY_BROKER_URL: Optional[str] = Field(..., validation_alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, validation_alias="CELERY_RESULT_BACKEND")

    CELERY_BROKER_TYPE: Optional[QueueType] = Field(None, validation_alias="CELERY_BROKER_TYPE")
    CELERY_REDIS_BROKER_URL: Optional[str] = Field(None, validation_alias="CELERY_REDIS_BROKER_URL")
    CELERY_REDIS_BACKEND_URL: Optional[str] = Field(
        None, validation_alias="CELERY_REDIS_BACKEND_URL"
    )
    CELERY_SQS_BROKER_URL: Optional[str] = Field(None, validation_alias="CELERY_SQS_BROKER_URL")
    CELERY_RABBIT_BROKER_URL: Optional[str] = Field(
        None, validation_alias="CELERY_RABBIT_BROKER_URL"
    )
    CELERY_RABBIT_BACKEND_URL: Optional[str] = Field(
        None, validation_alias="CELERY_RABBIT_BACKEND_URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def load_celery_beat_schedule(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schedule_path = os.path.join(base_dir, "celery_beat_schedule.yaml")

            with open(schedule_path, "r") as file:
                beat_schedule = yaml.safe_load(file)

                for key, value in beat_schedule.items():
                    if (
                        "schedule" in value
                        and isinstance(value["schedule"], dict)
                        and "crontab" in value["schedule"]
                    ):
                        value["schedule"] = crontab(**value["schedule"]["crontab"])

                for key, value in beat_schedule.items():
                    if "schedule" not in value:
                        logger.error(f"Task {key} is missing a schedule definition.")
                        raise ValueError(f"Task {key} is missing a schedule definition.")

                logger.info("Celery beat schedule loaded successfully.")
                return beat_schedule

        except FileNotFoundError as e:
            logger.error(f"Celery beat schedule file not found: {e}")
        except ValidationError as e:
            logger.error(f"Error validating the celery beat schedule: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading celery beat schedule: {e}")

        return {}

    @property
    def CELERY_BEAT_SCHEDULE(self):
        return self.load_celery_beat_schedule()

    def validate(self):
        try:
            if not self.CELERY_BROKER_URL:
                logger.error("CELERY_BROKER_URL is not set.")
                raise ValueError("CELERY_BROKER_URL is not set.")
            if not self.CELERY_BEAT_SCHEDULE:
                logger.warning(
                    "CELERY_BEAT_SCHEDULE is not set. Celery tasks might not run on a schedule."
                )
        except ValidationError as e:
            logger.error(f"Validation error in settings: {e}")
            raise ValueError(f"Validation error in settings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during settings validation: {e}")
            raise ValueError(f"Unexpected error during settings validation: {e}")


celery_settings = CelerySettings()
