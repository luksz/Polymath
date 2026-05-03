import uuid
from datetime import date

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from polymath_core.errors import NotFoundError

from ..infra.db.models import Post, ReadingLogEntry
from ..infra.db.repos import PostRepository, ReadingLogRepository

logger = structlog.get_logger()

_post_repo = PostRepository()
_reading_log_repo = ReadingLogRepository()


class PostService:
    def __init__(self, repo: PostRepository | None = None) -> None:
        self._repo = repo or _post_repo

    async def create_post(
        self,
        session: AsyncSession,
        slug: str,
        kind: str,
        title: str,
        body_mdx: str,
        summary: str | None = None,
        tags: list[str] | None = None,
        cover_image_url: str | None = None,
    ) -> Post:
        post = await self._repo.create(
            session,
            slug=slug,
            kind=kind,
            title=title,
            body_mdx=body_mdx,
            summary=summary,
            tags=tags,
            cover_image_url=cover_image_url,
        )
        logger.info("post.created", slug=slug, kind=kind, post_id=str(post.id))
        return post

    async def get_post(self, session: AsyncSession, slug: str) -> Post:
        post = await self._repo.get_by_slug(session, slug)
        if post is None:
            raise NotFoundError(f"Post with slug '{slug}' not found")
        return post

    async def list_posts(
        self,
        session: AsyncSession,
        kind: str | None = None,
        tag: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Post]:
        return await self._repo.list_posts(
            session, kind=kind, tag=tag, status="published", limit=limit, offset=offset
        )

    async def update_post(
        self,
        session: AsyncSession,
        post_id: uuid.UUID,
        **fields: object,
    ) -> Post:
        post = await self._repo.update(session, post_id, **fields)
        if post is None:
            raise NotFoundError(f"Post '{post_id}' not found")
        logger.info("post.updated", post_id=str(post_id))
        return post

    async def publish_post(self, session: AsyncSession, post_id: uuid.UUID) -> Post:
        post = await self._repo.get_by_id(session, post_id)
        if post is None:
            raise NotFoundError(f"Post '{post_id}' not found")

        word_count = len(post.body_mdx.split())
        reading_minutes = max(1, word_count // 200)
        post.reading_minutes = reading_minutes

        published = await self._repo.publish(session, post_id)
        if published is None:
            raise NotFoundError(f"Post '{post_id}' not found")

        logger.info(
            "post.published",
            post_id=str(post_id),
            reading_minutes=reading_minutes,
        )
        return published


class ReadingLogService:
    def __init__(self, repo: ReadingLogRepository | None = None) -> None:
        self._repo = repo or _reading_log_repo

    async def add_entry(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        url: str | None = None,
        source: str | None = None,
        finished_on: date | None = None,
        rating: int | None = None,
        notes_md: str | None = None,
        tags: list[str] | None = None,
    ) -> ReadingLogEntry:
        entry = await self._repo.create(
            session,
            user_id=user_id,
            title=title,
            url=url,
            source=source,
            finished_on=finished_on,
            rating=rating,
            notes_md=notes_md,
            tags=tags,
        )
        logger.info("reading_log.entry_added", user_id=user_id, title=title)
        return entry

    async def list_entries(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReadingLogEntry]:
        return await self._repo.list_entries(session, limit=limit, offset=offset)
