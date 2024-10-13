import logging
import traceback
from typing import Dict, Union
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    APP_NAME: str = Field("Jambu-Integrator", validation_alias="APP_NAME")
    OPENAI_API_KEY: str = Field(..., validation_alias="OPENAI_API_KEY")
    OPENAI_ORG_ID: str = Field(..., validation_alias="OPENAI_ORG_ID")
    SUPABASE_URL: str = Field(..., validation_alias="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., validation_alias="SUPABASE_KEY")
    SUPABASE_BUCKET_NAME: str = Field(..., validation_alias="SUPABASE_BUCKET_NAME")
    RATE_LIMIT_MAX_REQUESTS: int = Field(1000, validation_alias="RATE_LIMIT_MAX_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(60, validation_alias="RATE_LIMIT_PERIOD")
    HASH_IPS: bool = Field(False, validation_alias="HASH_IPS")

    # Database settings
    # DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    POSTGRES_USER: str = Field(..., validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(..., validation_alias="POSTGRES_HOST")
    POSTGRES_DB: str = Field(..., validation_alias="POSTGRES_DB")
    POSTGRES_PORT: str = Field(..., validation_alias="POSTGRES_PORT")

    #  Security
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Queue settings
    QUEUE_USERNAME: str = Field(..., validation_alias="QUEUE_USERNAME")
    QUEUE_PASSWORD: str = Field(..., validation_alias="QUEUE_PASSWORD")

    # Queue settings
    TAVILY_API_KEY: str = Field(..., validation_alias="TAVILY_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{quote_plus(self.POSTGRES_USER)}:"
            f"{quote_plus(self.POSTGRES_PASSWORD)}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def CELERY_BEAT_SCHEDULE(self):
        try:
            from api_template.celery.config.celery_settings import CelerySettings

            return CelerySettings().CELERY_BEAT_SCHEDULE
        except Exception as e:
            logger.error(f"Misconfigured Celery settings: {e} - {traceback.format_exc()}")
            return {}

    @property
    def api_description(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "title": "API Template",
            "description": "The API Template is a tool for developers to streamline "
            "the process of creating APIs.",
            "version": "0.0.1",
            "contact": {
                "email": "<setin@tcepa.tc.br>",
            },
            "license_info": {
                "name": "@ 2024 TCE-PA",
                "url": "https://www.tcepa.tc.br",
            },
        }


settings = Settings()
