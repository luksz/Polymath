from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    service_name: str = Field(default="polymath-service")

    database_url: str = Field(
        default="postgresql+asyncpg://polymath:polymath@localhost:5433/polymath"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    sentry_dsn: str = Field(default="")

    polymath_service_secret: str = Field(default="dev-secret-changeme")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
