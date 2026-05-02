from pydantic import Field
from polymath_core.config import Settings as BaseSettings


class GatewaySettings(BaseSettings):
    service_name: str = "gateway"

    clerk_secret_key: str = Field(default="")
    clerk_publishable_key: str = Field(default="")

    # Internal service URLs
    llm_gateway_url: str = Field(default="http://llm-gateway:8001")
    notes_svc_url: str = Field(default="http://notes-svc:8002")
    habits_svc_url: str = Field(default="http://habits-svc:8003")
    content_svc_url: str = Field(default="http://content-svc:8004")
    analytics_svc_url: str = Field(default="http://analytics-svc:8005")
    games_svc_url: str = Field(default="http://games-svc:8006")
    jobs_svc_url: str = Field(default="http://jobs-svc:8007")

    # Timeout config (seconds)
    default_timeout: float = Field(default=5.0)
    llm_timeout: float = Field(default=30.0)

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60)
