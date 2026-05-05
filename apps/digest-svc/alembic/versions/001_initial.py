"""initial digest schema

Revision ID: 001
Revises:
Create Date: 2026-05-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create digest schema (idempotent)
    op.execute("CREATE SCHEMA IF NOT EXISTS digest")

    # Create digest.digests table
    op.execute("""
        CREATE TABLE IF NOT EXISTS digest.digests (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            for_date    DATE NOT NULL UNIQUE,
            topic_tags  TEXT[] NOT NULL,
            status      TEXT NOT NULL DEFAULT 'pending',
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Create digest.papers table
    op.execute("""
        CREATE TABLE IF NOT EXISTS digest.papers (
            id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            digest_id         UUID NOT NULL REFERENCES digest.digests(id) ON DELETE CASCADE,
            arxiv_id          TEXT NOT NULL,
            title             TEXT NOT NULL,
            authors           TEXT[] NOT NULL,
            abstract          TEXT NOT NULL,
            arxiv_url         TEXT NOT NULL,
            relevance_score   INTEGER NOT NULL,
            summary_headline  TEXT NOT NULL,
            summary_body      TEXT NOT NULL,
            key_insight       TEXT NOT NULL,
            why_it_matters    TEXT NOT NULL,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Index on papers(digest_id)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_papers_digest_id "
        "ON digest.papers (digest_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS digest.papers")
    op.execute("DROP TABLE IF EXISTS digest.digests")
    op.execute("DROP SCHEMA IF EXISTS digest")
