from polymath_core.config import Settings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class HabitsSvcSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = Field(default="habits-svc")
