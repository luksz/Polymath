import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CompletionMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class CompleteRequestSchema(BaseModel):
    model: str = "claude-sonnet-4-6"
    messages: list[CompletionMessageSchema]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=100_000)
    stream: bool = False
    use_cache: bool = True


class CompleteResponseSchema(BaseModel):
    run_id: uuid.UUID
    model: str
    content: str
    input_tokens: int
    output_tokens: int
    cost_micro_usd: int
    latency_ms: int
    cache_hit: bool
    finish_reason: str


class PromptCreateSchema(BaseModel):
    slug: str
    description: str | None = None


class PromptVersionCreateSchema(BaseModel):
    template: str
    variables: dict[str, Any] = Field(default_factory=dict)
    default_model: str = "claude-sonnet-4-6"
    default_params: dict[str, Any] = Field(
        default_factory=lambda: {"temperature": 0.7, "max_tokens": 2048}
    )
    notes: str | None = None


class PromptSchema(BaseModel):
    id: uuid.UUID
    slug: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptVersionSchema(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    version: int
    template: str
    variables: dict[str, Any]
    default_model: str
    default_params: dict[str, Any]
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmbedRequestSchema(BaseModel):
    input: list[str]
    model: str = "text-embedding-3-small"


class EmbedResponseSchema(BaseModel):
    model: str
    embeddings: list[list[float]]
    input_tokens: int
    cost_micro_usd: int


class UsageSummarySchema(BaseModel):
    total_runs: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_micro_usd: int
    budget_daily_micro_usd: int
    budget_monthly_micro_usd: int
    spent_today_micro_usd: int
    spent_this_month_micro_usd: int
