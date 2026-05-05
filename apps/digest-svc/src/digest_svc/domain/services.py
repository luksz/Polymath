import asyncio
import uuid
from datetime import date

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from polymath_core.errors import NotFoundError

from ..infra.arxiv_client import ArxivClient
from ..infra.db.models import Digest, DigestPaper
from ..infra.db.repos import DigestRepository, PaperRepository
from ..infra.llm_client import DigestLLMClient

logger = structlog.get_logger()


class DigestService:
    def __init__(self, llm_gateway_url: str = "http://localhost:8011") -> None:
        self._digest_repo = DigestRepository()
        self._paper_repo = PaperRepository()
        self._arxiv = ArxivClient()
        self._llm = DigestLLMClient(llm_gateway_url)

    async def run_digest(
        self,
        session: AsyncSession,
        topic_list: list[str],
        papers_to_fetch: int = 20,
        papers_to_summarise: int = 5,
    ) -> Digest:
        """Full pipeline: fetch -> score -> top-N -> summarise -> persist."""
        today = date.today()

        # Step 1: idempotency check
        existing = await self._digest_repo.get_by_date(session, today)
        if existing is not None:
            logger.info("digest.already_exists", for_date=str(today), digest_id=str(existing.id))
            return existing

        # Step 2: create a new Digest record with status='running'
        digest = await self._digest_repo.create(session, today, topic_list)
        await self._digest_repo.update_status(session, digest.id, "running")
        logger.info("digest.started", digest_id=str(digest.id), for_date=str(today))

        try:
            # Step 3: fetch papers from arXiv
            papers = await self._arxiv.fetch_recent(topic_list, papers_to_fetch)
            logger.info("digest.papers_fetched", count=len(papers), digest_id=str(digest.id))

            # Step 4: score papers concurrently
            scores: list[int] = await asyncio.gather(
                *[self._llm.score_relevance(p.title, p.abstract) for p in papers]
            )

            # Step 5: sort by score descending, take top N
            scored = sorted(zip(papers, scores), key=lambda x: x[1], reverse=True)
            top_papers = scored[:papers_to_summarise]
            logger.info(
                "digest.top_papers_selected",
                count=len(top_papers),
                digest_id=str(digest.id),
            )

            # Step 6: summarise top papers concurrently
            summaries: list[dict[str, str]] = await asyncio.gather(
                *[self._llm.summarise(p.title, p.abstract) for p, _ in top_papers]
            )

            # Step 7: persist each paper
            for (paper, score), summary in zip(top_papers, summaries):
                await self._paper_repo.create_paper(
                    session=session,
                    digest_id=digest.id,
                    arxiv_id=paper.arxiv_id,
                    title=paper.title,
                    authors=paper.authors,
                    abstract=paper.abstract,
                    arxiv_url=paper.arxiv_url,
                    relevance_score=score,
                    summary_headline=summary["headline"],
                    summary_body=summary["body_md"],
                    key_insight=summary["key_insight"],
                    why_it_matters=summary["why_it_matters"],
                )

            # Step 8: update digest status to 'done'
            await self._digest_repo.update_status(session, digest.id, "done")
            await session.refresh(digest)
            logger.info("digest.completed", digest_id=str(digest.id), for_date=str(today))
            return digest

        except Exception:
            # Step 10: on any exception, update status to 'failed' and re-raise
            await self._digest_repo.update_status(session, digest.id, "failed")
            logger.exception("digest.failed", digest_id=str(digest.id))
            raise

    async def get_today(self, session: AsyncSession) -> Digest | None:
        return await self._digest_repo.get_by_date(session, date.today())

    async def get_by_date(self, session: AsyncSession, date_str: str) -> Digest:
        try:
            for_date = date.fromisoformat(date_str)
        except ValueError:
            raise NotFoundError(
                f"Invalid date format: {date_str!r}",
                instance=f"/v1/digests/{date_str}",
            )
        digest = await self._digest_repo.get_by_date(session, for_date)
        if digest is None:
            raise NotFoundError(
                f"No digest found for {date_str}",
                instance=f"/v1/digests/{date_str}",
            )
        return digest

    async def list_digests(self, session: AsyncSession, limit: int = 30) -> list[Digest]:
        return await self._digest_repo.list_digests(session, limit)

    async def get_papers(self, session: AsyncSession, digest_id: uuid.UUID) -> list[DigestPaper]:
        return await self._paper_repo.list_papers(session, digest_id)
