import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from polymath_core.errors import NotFoundError

from content_svc.domain.services import PostService
from content_svc.infra.db.repos import PostRepository


@pytest.mark.asyncio
async def test_get_post_raises_not_found():
    repo = MagicMock(spec=PostRepository)
    repo.get_by_slug = AsyncMock(return_value=None)

    service = PostService(repo=repo)
    session = MagicMock()

    with pytest.raises(NotFoundError):
        await service.get_post(session, "nonexistent-slug")

    repo.get_by_slug.assert_called_once_with(session, "nonexistent-slug")


@pytest.mark.asyncio
async def test_publish_sets_reading_minutes():
    post_id = uuid.uuid4()
    # 400 words => 400 // 200 = 2 reading minutes
    body = " ".join(["word"] * 400)

    mock_post = MagicMock()
    mock_post.id = post_id
    mock_post.body_mdx = body
    mock_post.reading_minutes = None

    published_post = MagicMock()
    published_post.reading_minutes = 2

    repo = MagicMock(spec=PostRepository)
    repo.get_by_id = AsyncMock(return_value=mock_post)
    repo.publish = AsyncMock(return_value=published_post)

    service = PostService(repo=repo)
    session = MagicMock()

    result = await service.publish_post(session, post_id)

    assert mock_post.reading_minutes == 2
    repo.publish.assert_called_once_with(session, post_id)
    assert result is published_post
