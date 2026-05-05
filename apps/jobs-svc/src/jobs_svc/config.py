from polymath_core.config import Settings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class JobsSvcSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = Field(default="jobs-svc")
    digest_svc_url: str = Field(default="http://localhost:8015")
    digest_cron_hour: int = Field(default=7)
    digest_cron_minute: int = Field(default=0)
