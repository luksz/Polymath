import uuid
from typing import Literal

import httpx
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from polymath_core.errors import NotFoundError

from ..infra.db.models import Note
from ..infra.db.repos import NoteRepository

logger = structlog.get_logger()


class NoteService:
    def __init__(self, llm_gateway_url: str = "http://localhost:8001") -> None:
        self._repo = NoteRepository()
        self._llm_gateway_url = llm_gateway_url

    async def create_note(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        body_md: str,
        tags: list[str],
    ) -> Note:
        note = await self._repo.create(session, user_id, title, body_md, tags)
        logger.info("note.created", note_id=str(note.id), user_id=user_id)
        return note

    async def get_note(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
    ) -> Note:
        note = await self._repo.get(session, note_id, user_id)
        if note is None:
            raise NotFoundError(f"Note {note_id} not found", instance=f"/v1/notes/{note_id}")
        return note

    async def list_notes(
        self,
        session: AsyncSession,
        user_id: str,
        q: str | None = None,
        tag: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Note]:
        return await self._repo.list_notes(session, user_id, q=q, tag=tag, limit=limit, offset=offset)

    async def update_note(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
        **fields: object,
    ) -> Note:
        note = await self._repo.update(session, note_id, user_id, **fields)
        if note is None:
            raise NotFoundError(f"Note {note_id} not found", instance=f"/v1/notes/{note_id}")
        logger.info("note.updated", note_id=str(note_id), user_id=user_id)
        return note

    async def delete_note(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        user_id: str,
    ) -> None:
        deleted = await self._repo.delete(session, note_id, user_id)
        if not deleted:
            raise NotFoundError(f"Note {note_id} not found", instance=f"/v1/notes/{note_id}")
        logger.info("note.deleted", note_id=str(note_id), user_id=user_id)

    async def search_notes(
        self,
        session: AsyncSession,
        user_id: str,
        query: str,
        mode: Literal["fts", "semantic", "hybrid"] = "fts",
    ) -> list[Note]:
        if mode == "fts":
            return await self._repo.search_fts(session, user_id, query)

        # For semantic and hybrid, attempt to get an embedding from the LLM gateway
        embedding: list[float] | None = None
        try:
            embedding = await self._get_embedding(query)
        except Exception as exc:
            logger.warning(
                "note.search.embedding_failed",
                error=str(exc),
                fallback="fts",
                mode=mode,
            )

        if embedding is None:
            # Fall back to FTS when embedding unavailable
            return await self._repo.search_fts(session, user_id, query)

        if mode == "semantic":
            return await self._repo.search_semantic(session, user_id, embedding)

        # hybrid: run both and merge (deduplicate, semantic results first)
        semantic_results = await self._repo.search_semantic(session, user_id, embedding, limit=10)
        fts_results = await self._repo.search_fts(session, user_id, query, limit=10)
        seen: set[uuid.UUID] = set()
        merged: list[Note] = []
        for note in semantic_results + fts_results:
            if note.id not in seen:
                seen.add(note.id)
                merged.append(note)
        return merged[:10]

    async def _get_embedding(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._llm_gateway_url}/v1/embed",
                json={"input": [text]},
            )
            response.raise_for_status()
            data = response.json()
            embeddings: list[list[float]] = data["embeddings"]
            return embeddings[0]
