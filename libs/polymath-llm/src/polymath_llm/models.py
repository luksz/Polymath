from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class CompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1)
    stream: bool = False
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    use_cache: bool = True
    use_semantic_cache: bool = False


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    id: str
    model: str
    content: str
    usage: Usage
    cost_micro_usd: int
    cache_hit: bool = False
    latency_ms: int = 0
    finish_reason: str = "stop"


class EmbeddingRequest(BaseModel):
    model: str = "text-embedding-3-small"
    input: list[str]


class EmbeddingResponse(BaseModel):
    model: str
    embeddings: list[list[float]]
    usage: Usage
    cost_micro_usd: int
