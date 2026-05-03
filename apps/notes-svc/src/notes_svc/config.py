from polymath_core.config import Settings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class NotesSvcSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = Field(default="notes-svc")
    llm_gateway_url: str = Field(default="http://localhost:8001")
