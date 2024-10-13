from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        extra = "ignore"


security_settings = SecuritySettings()
