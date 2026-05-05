import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_db, get_digest_service, get_settings
from ...domain.services import DigestService
from .schemas import DigestListItem, DigestPaperResponse, DigestResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/v1/digests", tags=["digests"])


def _require_user_id(
    x_polymath_user_id: Annotated[str | None, Header(alias="X-Polymath-User-Id")] = None,
) -> str:
    if not x_polymath_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Polymath-User-Id header",
        )
    return x_polymath_user_id


@router.get("", response_model=list[DigestListItem])
async def list_digests(
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: DigestService = Depends(get_digest_service),
) -> list[DigestListItem]:
    digests = await svc.list_digests(db, limit=30)
    return [
        DigestListItem(
            id=d.id,
            for_date=d.for_date,
            status=d.status,
            paper_count=len(d.papers),
            created_at=d.created_at,
        )
        for d in digests
    ]


@router.get("/today", response_model=DigestResponse)
async def get_today(
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: DigestService = Depends(get_digest_service),
) -> DigestResponse:
    digest = await svc.get_today(db)
    if digest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No digest has been run for today yet.",
        )
    papers = await svc.get_papers(db, digest.id)
    response = DigestResponse.model_validate(digest)
    response.papers = [DigestPaperResponse.model_validate(p) for p in papers]
    return response


@router.get("/{date}", response_model=DigestResponse)
async def get_by_date(
    date: str,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: DigestService = Depends(get_digest_service),
) -> DigestResponse:
    digest = await svc.get_by_date(db, date)
    papers = await svc.get_papers(db, digest.id)
    response = DigestResponse.model_validate(digest)
    response.papers = [DigestPaperResponse.model_validate(p) for p in papers]
    return response


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_run(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(_require_user_id),
    svc: DigestService = Depends(get_digest_service),
) -> dict[str, str]:
    settings = get_settings()

    async def _run() -> None:
        from ...deps import _get_session_factory

        async with _get_session_factory()() as session:
            try:
                await svc.run_digest(
                    session,
                    topic_list=settings.topic_list,
                    papers_to_fetch=settings.papers_to_fetch,
                    papers_to_summarise=settings.papers_to_summarise,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("digest.background_run_failed")

    background_tasks.add_task(_run)
    logger.info("digest.run_triggered", triggered_by=user_id)
    return {"status": "started"}


@router.get("/{date}/papers/{paper_id}", response_model=DigestPaperResponse)
async def get_paper(
    date: str,
    paper_id: uuid.UUID,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: DigestService = Depends(get_digest_service),
) -> DigestPaperResponse:
    # Validate the date and digest exist
    digest = await svc.get_by_date(db, date)
    papers = await svc.get_papers(db, digest.id)
    paper = next((p for p in papers if p.id == paper_id), None)
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper {paper_id} not found in digest for {date}.",
        )
    return DigestPaperResponse.model_validate(paper)
