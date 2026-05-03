import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Post, ReadingLogEntry


class PostRepository:
    async def create(
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
        post = Post(
            slug=slug,
            kind=kind,
            title=title,
            body_mdx=body_mdx,
            summary=summary,
            tags=tags or [],
            cover_image_url=cover_image_url,
        )
        session.add(post)
        await session.flush()
        await session.refresh(post)
        return post

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Post | None:
        result = await session.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_id(
        self, session: AsyncSession, post_id: uuid.UUID
    ) -> Post | None:
        result = await session.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        session: AsyncSession,
        kind: str | None = None,
        tag: str | None = None,
        status: str = "published",
        limit: int = 20,
        offset: int = 0,
    ) -> list[Post]:
        stmt = select(Post).where(Post.status == status)
        if kind is not None:
            stmt = stmt.where(Post.kind == kind)
        if tag is not None:
            stmt = stmt.where(Post.tags.contains([tag]))
        stmt = stmt.order_by(Post.published_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        post_id: uuid.UUID,
        **fields: Any,
    ) -> Post | None:
        post = await self.get_by_id(session, post_id)
        if post is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(post, key, value)
        await session.flush()
        await session.refresh(post)
        return post

    async def publish(
        self, session: AsyncSession, post_id: uuid.UUID
    ) -> Post | None:
        post = await self.get_by_id(session, post_id)
        if post is None:
            return None
        post.status = "published"
        post.published_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(post)
        return post


class ReadingLogRepository:
    async def create(
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
        entry = ReadingLogEntry(
            user_id=user_id,
            title=title,
            url=url,
            source=source,
            finished_on=finished_on,
            rating=rating,
            notes_md=notes_md,
            tags=tags or [],
        )
        session.add(entry)
        await session.flush()
        await session.refresh(entry)
        return entry

    async def list_entries(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReadingLogEntry]:
        result = await session.execute(
            select(ReadingLogEntry)
            .order_by(ReadingLogEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
