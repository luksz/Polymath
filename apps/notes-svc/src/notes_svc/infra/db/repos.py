import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Note


class NoteRepository:
    async def create(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        body_md: str,
        tags: list[str],
    ) -> Note:
        note = Note(
            user_id=user_id,
            title=title,
            body_md=body_md,
            tags=tags,
        )
        session.add(note)
        await session.flush()
        await session.refresh(note)
        return note

    async def get(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
    ) -> Note | None:
        result = await session.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_notes(
        self,
        session: AsyncSession,
        user_id: str,
        q: str | None = None,
        tag: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == user_id, Note.deleted_at.is_(None))
        )
        if q:
            stmt = stmt.where(Note.title.ilike(f"%{q}%") | Note.body_md.ilike(f"%{q}%"))
        if tag:
            stmt = stmt.where(Note.tags.contains([tag]))
        stmt = stmt.order_by(Note.updated_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
        **fields: object,
    ) -> Note | None:
        note = await self.get(session, note_id, user_id)
        if note is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(note, key, value)
        note.updated_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(note)
        return note

    async def delete(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
    ) -> bool:
        note = await self.get(session, note_id, user_id)
        if note is None:
            return False
        note.deleted_at = datetime.now(timezone.utc)
        await session.flush()
        return True

    async def search_fts(
        self,
        session: AsyncSession,
        user_id: str,
        query: str,
        limit: int = 10,
    ) -> list[Note]:
        tsquery = func.plainto_tsquery(text("'english'"), query)
        tsvector = func.to_tsvector(text("'english'"), Note.title + " " + Note.body_md)
        result = await session.execute(
            select(Note)
            .where(
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
                tsvector.op("@@")(tsquery),
            )
            .order_by(Note.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_embedding(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        embedding: list[float],
    ) -> None:
        note = await session.get(Note, note_id)
        if note is not None:
            note.embedding = embedding  # type: ignore[assignment]
            await session.flush()

    async def search_semantic(
        self,
        session: AsyncSession,
        user_id: str,
        embedding: list[float],
        limit: int = 10,
    ) -> list[Note]:
        result = await session.execute(
            select(Note)
            .where(
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
                Note.embedding.is_not(None),
            )
            .order_by(Note.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return list(result.scalars().all())
