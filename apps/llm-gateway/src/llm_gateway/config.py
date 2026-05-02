from pydantic import Field

from polymath_core.config import Settings as BaseSettings


class LLMGatewaySettings(BaseSettings):
    service_name: str = "llm-gateway"

    anthropic_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    voyage_api_key: str = Field(default="")

    default_daily_limit_micro_usd: int = Field(default=5_000_000)    # $5/day
    default_monthly_limit_micro_usd: int = Field(default=100_000_000)  # $100/mo

    exact_cache_ttl: int = Field(default=86400)
    semantic_cache_threshold: float = Field(default=0.97)
