from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from polymath_llm import LLMClient, CompletionRequest, Message

from ...deps import get_db, get_llm_client, get_user_id
from ...infra.db.repos import RunRepository
from .schemas import CompleteRequestSchema, CompleteResponseSchema

router = APIRouter()


def _provider_from_model(model: str) -> str:
    if model.startswith("claude"):
        return "anthropic"
    if any(model.startswith(p) for p in ("gpt", "o1", "o3")):
        return "openai"
    return "unknown"


@router.post("", response_model=CompleteResponseSchema)
async def complete(
    body: CompleteRequestSchema,
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client),
    user_id: str | None = Depends(get_user_id),
) -> CompleteResponseSchema:
    req = CompletionRequest(
        model=body.model,
        messages=[Message(role=m.role, content=m.content) for m in body.messages],
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        stream=False,
        use_cache=body.use_cache,
    )
    response = await llm.complete(req)

    run_repo = RunRepository(db)
    run_id = await run_repo.create_run(
        user_id=user_id,
        model=body.model,
        provider=_provider_from_model(body.model),
        input={"messages": [m.model_dump() for m in body.messages]},
        output={"content": response.content},
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost_micro_usd=response.cost_micro_usd,
        latency_ms=response.latency_ms,
        status="ok",
        cache_hit=response.cache_hit,
    )

    return CompleteResponseSchema(
        run_id=run_id,
        model=response.model,
        content=response.content,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost_micro_usd=response.cost_micro_usd,
        latency_ms=response.latency_ms,
        cache_hit=response.cache_hit,
        finish_reason=response.finish_reason,
    )


@router.post("/stream")
async def complete_stream(
    body: CompleteRequestSchema,
    llm: LLMClient = Depends(get_llm_client),
) -> StreamingResponse:
    req = CompletionRequest(
        model=body.model,
        messages=[Message(role=m.role, content=m.content) for m in body.messages],
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        stream=True,
    )

    async def event_stream():  # type: ignore[no-untyped-def]
        async for chunk in llm.stream(req):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
