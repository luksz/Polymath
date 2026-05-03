from fastapi import APIRouter, Depends, Request, Response

from ...config import GatewaySettings
from ...deps import get_settings, require_user
from ...infra.clients.notes_client import NotesClient

router = APIRouter()


def get_notes_client(settings: GatewaySettings = Depends(get_settings)) -> NotesClient:
    return NotesClient(
        base_url=settings.notes_svc_url,
        service_secret=settings.polymath_service_secret,
        timeout=settings.default_timeout,
    )


@router.get("")
async def list_notes(
    q: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> dict:
    return await notes.list_notes(user_id=user_id, q=q, tag=tag, limit=limit, offset=offset)


@router.post("")
async def create_note(
    request: Request,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> dict:
    return await notes.create_note(user_id=user_id, payload=await request.json())


@router.get("/{note_id}")
async def get_note(
    note_id: str,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> dict:
    return await notes.get_note(user_id=user_id, note_id=note_id)


@router.put("/{note_id}")
async def update_note(
    note_id: str,
    request: Request,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> dict:
    return await notes.update_note(user_id=user_id, note_id=note_id, payload=await request.json())


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: str,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> Response:
    await notes.delete_note(user_id=user_id, note_id=note_id)
    return Response(status_code=204)


@router.post("/search")
async def search_notes(
    request: Request,
    user_id: str = Depends(require_user),
    notes: NotesClient = Depends(get_notes_client),
) -> list:
    return await notes.search_notes(user_id=user_id, payload=await request.json())
