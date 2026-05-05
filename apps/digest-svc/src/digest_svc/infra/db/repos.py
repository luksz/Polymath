import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Digest, DigestPaper


class DigestRepository:
    async def create(
        self,
        session: AsyncSession,
        for_date: date,
        topic_tags: list[str],
    ) -> Digest:
        digest = Digest(for_date=for_date, topic_tags=topic_tags, status="pending")
        session.add(digest)
        await session.flush()
        await session.refresh(digest)
        return digest

    async def get_by_date(
        self,
        session: AsyncSession,
        for_date: date,
    ) -> Digest | None:
        result = await session.execute(
            select(Digest).where(Digest.for_date == for_date)
        )
        return result.scalar_one_or_none()

    async def list_digests(
        self,
        session: AsyncSession,
        limit: int = 30,
    ) -> list[Digest]:
        result = await session.execute(
            select(Digest).order_by(Digest.for_date.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        session: AsyncSession,
        digest_id: uuid.UUID,
        status: str,
    ) -> None:
        digest = await session.get(Digest, digest_id)
        if digest is not None:
            digest.status = status
            await session.flush()


class PaperRepository:
    async def create_paper(
        self,
        session: AsyncSession,
        digest_id: uuid.UUID,
        arxiv_id: str,
        title: str,
        authors: list[str],
        abstract: str,
        arxiv_url: str,
        relevance_score: int,
        summary_headline: str,
        summary_body: str,
        key_insight: str,
        why_it_matters: str,
    ) -> DigestPaper:
        paper = DigestPaper(
            digest_id=digest_id,
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            arxiv_url=arxiv_url,
            relevance_score=relevance_score,
            summary_headline=summary_headline,
            summary_body=summary_body,
            key_insight=key_insight,
            why_it_matters=why_it_matters,
        )
        session.add(paper)
        await session.flush()
        await session.refresh(paper)
        return paper

    async def list_papers(
        self,
        session: AsyncSession,
        digest_id: uuid.UUID,
    ) -> list[DigestPaper]:
        result = await session.execute(
            select(DigestPaper)
            .where(DigestPaper.digest_id == digest_id)
            .order_by(DigestPaper.relevance_score.desc())
        )
        return list(result.scalars().all())

    async def get_paper(
        self,
        session: AsyncSession,
        paper_id: uuid.UUID,
    ) -> DigestPaper | None:
        return await session.get(DigestPaper, paper_id)
