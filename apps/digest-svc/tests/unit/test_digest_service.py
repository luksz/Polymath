import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from digest_svc.domain.services import DigestService
from digest_svc.infra.arxiv_client import ArxivClient
from digest_svc.infra.db.models import Digest
from digest_svc.infra.db.repos import DigestRepository


@pytest.fixture
def svc() -> DigestService:
    return DigestService(llm_gateway_url="http://localhost:8011")


@pytest.mark.asyncio
async def test_run_is_idempotent(svc: DigestService) -> None:
    """If a digest already exists for today, run_digest returns it without re-running."""
    existing_digest = Digest(
        id=uuid.uuid4(),
        for_date=date.today(),
        topic_tags=["cs.AI"],
        status="done",
        created_at=datetime.now(timezone.utc),
    )

    # Patch the digest repo's get_by_date to return the existing digest
    svc._digest_repo = MagicMock(spec=DigestRepository)
    svc._digest_repo.get_by_date = AsyncMock(return_value=existing_digest)

    mock_session = AsyncMock()

    result = await svc.run_digest(
        session=mock_session,
        topic_list=["cs.AI"],
        papers_to_fetch=5,
        papers_to_summarise=2,
    )

    assert result is existing_digest
    # create should NOT have been called since we short-circuited
    svc._digest_repo.create.assert_not_called()


def test_arxiv_parse() -> None:
    """ArxivClient._parse_atom correctly parses a minimal valid Atom XML response."""
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <title>  Test Paper Title  </title>
    <summary>This is the abstract of the test paper.</summary>
    <author>
      <name>Alice Smith</name>
    </author>
    <author>
      <name>Bob Jones</name>
    </author>
  </entry>
</feed>"""

    client = ArxivClient()
    papers = client._parse_atom(xml_text)

    assert len(papers) >= 1
    paper = papers[0]
    assert paper.arxiv_id == "2401.00001v1"
    assert paper.title == "Test Paper Title"
    assert "Alice Smith" in paper.authors
    assert "Bob Jones" in paper.authors
    assert paper.abstract == "This is the abstract of the test paper."
    assert "2401.00001v1" in paper.arxiv_url
