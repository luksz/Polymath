import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_db, get_note_service
from ...domain.services import NoteService
from .schemas import NoteCreate, NoteListResponse, NoteResponse, NoteSearchRequest, NoteUpdate

router = APIRouter(prefix="/v1/notes", tags=["notes"])


def _require_user_id(
    x_polymath_user_id: Annotated[str | None, Header(alias="X-Polymath-User-Id")] = None,
) -> str:
    if not x_polymath_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Polymath-User-Id header")
    return x_polymath_user_id


@router.get("", response_model=NoteListResponse)
async def list_notes(
    q: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> NoteListResponse:
    notes = await svc.list_notes(db, user_id, q=q, tag=tag, limit=limit, offset=offset)
    return NoteListResponse(items=[NoteResponse.model_validate(n) for n in notes], total=len(notes))


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    body: NoteCreate,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> NoteResponse:
    note = await svc.create_note(db, user_id, body.title, body.body_md, body.tags)
    return NoteResponse.model_validate(note)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> NoteResponse:
    note = await svc.get_note(db, note_id, user_id)
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    body: NoteUpdate,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> NoteResponse:
    note = await svc.update_note(
        db,
        note_id,
        user_id,
        **{k: v for k, v in body.model_dump().items() if v is not None},
    )
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: uuid.UUID,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> None:
    await svc.delete_note(db, note_id, user_id)


@router.post("/search", response_model=NoteListResponse)
async def search_notes(
    body: NoteSearchRequest,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
    svc: NoteService = Depends(get_note_service),
) -> NoteListResponse:
    notes = await svc.search_notes(db, user_id, body.query, body.mode)
    return NoteListResponse(items=[NoteResponse.model_validate(n) for n in notes], total=len(notes))
