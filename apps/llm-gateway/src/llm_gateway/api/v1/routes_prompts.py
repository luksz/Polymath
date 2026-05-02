from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_db
from ...infra.db.repos import PromptRepository
from .schemas import (
    PromptCreateSchema,
    PromptSchema,
    PromptVersionCreateSchema,
    PromptVersionSchema,
)

router = APIRouter()


@router.get("", response_model=list[PromptSchema])
async def list_prompts(db: AsyncSession = Depends(get_db)) -> list[PromptSchema]:
    repo = PromptRepository(db)
    return await repo.list_prompts()


@router.post("", response_model=PromptSchema, status_code=201)
async def create_prompt(
    body: PromptCreateSchema, db: AsyncSession = Depends(get_db)
) -> PromptSchema:
    repo = PromptRepository(db)
    return await repo.create_prompt(slug=body.slug, description=body.description)


@router.post("/{slug}/versions", response_model=PromptVersionSchema, status_code=201)
async def create_prompt_version(
    slug: str, body: PromptVersionCreateSchema, db: AsyncSession = Depends(get_db)
) -> PromptVersionSchema:
    repo = PromptRepository(db)
    prompt = await repo.get_prompt_by_slug(slug)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt '{slug}' not found")
    return await repo.create_version(prompt_id=prompt.id, **body.model_dump())


@router.get("/{slug}/versions/{version}", response_model=PromptVersionSchema)
async def get_prompt_version(
    slug: str, version: int, db: AsyncSession = Depends(get_db)
) -> PromptVersionSchema:
    repo = PromptRepository(db)
    pv = await repo.get_version(slug=slug, version=version)
    if not pv:
        raise HTTPException(
            status_code=404, detail=f"Prompt '{slug}' version {version} not found"
        )
    return pv
