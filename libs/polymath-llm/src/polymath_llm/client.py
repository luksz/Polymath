import hashlib
import json
import time
from typing import AsyncIterator

import litellm
from redis.asyncio import Redis

from .models import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Usage,
)
from .pricing import CostCalculator

CACHE_TTL = 86400  # 24 hours


class LLMClient:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._cost_calc = CostCalculator()

    def _cache_key(self, request: CompletionRequest) -> str:
        payload = {
            "model": request.model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        return f"llm:cache:{digest}"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if request.use_cache and not request.stream:
            key = self._cache_key(request)
            cached = await self._redis.get(key)
            if cached:
                response = CompletionResponse.model_validate_json(cached)
                response.cache_hit = True
                return response

        start = time.monotonic()
        raw = await litellm.acompletion(
            model=request.model,
            messages=[m.model_dump() for m in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        usage = Usage(
            input_tokens=raw.usage.prompt_tokens,
            output_tokens=raw.usage.completion_tokens,
            total_tokens=raw.usage.total_tokens,
        )
        cost = self._cost_calc.calculate(
            request.model, usage.input_tokens, usage.output_tokens
        )

        response = CompletionResponse(
            id=raw.id,
            model=raw.model,
            content=raw.choices[0].message.content or "",
            usage=usage,
            cost_micro_usd=cost,
            latency_ms=latency_ms,
            finish_reason=raw.choices[0].finish_reason or "stop",
        )

        if request.use_cache:
            key = self._cache_key(request)
            await self._redis.setex(key, CACHE_TTL, response.model_dump_json())

        return response

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        stream = await litellm.acompletion(
            model=request.model,
            messages=[m.model_dump() for m in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raw = await litellm.aembedding(model=request.model, input=request.input)
        usage = Usage(
            input_tokens=raw.usage.prompt_tokens,
            output_tokens=0,
            total_tokens=raw.usage.total_tokens,
        )
        cost = self._cost_calc.calculate(request.model, usage.input_tokens, 0)
        return EmbeddingResponse(
            model=request.model,
            embeddings=[item.embedding for item in raw.data],
            usage=usage,
            cost_micro_usd=cost,
        )
