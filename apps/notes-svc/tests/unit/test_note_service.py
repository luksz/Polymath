import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from polymath_core.errors import NotFoundError
from notes_svc.domain.services import NoteService
from notes_svc.infra.db.repos import NoteRepository


@pytest.fixture
def svc() -> NoteService:
    return NoteService(llm_gateway_url="http://localhost:8001")


@pytest.mark.asyncio
async def test_get_note_raises_not_found_when_repo_returns_none(svc: NoteService) -> None:
    """NoteService.get_note raises NotFoundError when the repository returns None."""
    note_id = uuid.uuid4()
    user_id = "user_test123"

    # Patch the repo's get method to return None
    svc._repo = MagicMock(spec=NoteRepository)
    svc._repo.get = AsyncMock(return_value=None)

    mock_session = AsyncMock()

    with pytest.raises(NotFoundError) as exc_info:
        await svc.get_note(mock_session, note_id, user_id)

    assert exc_info.value.status_code == 404
    assert str(note_id) in exc_info.value.detail
