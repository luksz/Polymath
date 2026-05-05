from polymath_core.config import Settings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class DigestSvcSettings(Settings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = Field(default="digest-svc")
    llm_gateway_url: str = Field(default="http://localhost:8011")
    digest_topics: str = Field(default="cs.AI,cs.LG,cs.CL,cs.CV,stat.ML")
    papers_to_fetch: int = Field(default=20)
    papers_to_summarise: int = Field(default=5)

    @property
    def topic_list(self) -> list[str]:
        return [t.strip() for t in self.digest_topics.split(",")]
