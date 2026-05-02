from fastapi import APIRouter, Depends

from polymath_llm import EmbeddingRequest, LLMClient

from ...deps import get_llm_client
from .schemas import EmbedRequestSchema, EmbedResponseSchema

router = APIRouter()


@router.post("", response_model=EmbedResponseSchema)
async def embed(
    body: EmbedRequestSchema, llm: LLMClient = Depends(get_llm_client)
) -> EmbedResponseSchema:
    req = EmbeddingRequest(model=body.model, input=body.input)
    response = await llm.embed(req)
    return EmbedResponseSchema(
        model=response.model,
        embeddings=response.embeddings,
        input_tokens=response.usage.input_tokens,
        cost_micro_usd=response.cost_micro_usd,
    )
