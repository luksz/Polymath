"""initial notes schema

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
    # Create notes schema (idempotent)
    op.execute("CREATE SCHEMA IF NOT EXISTS notes")

    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create notes.notes table
    op.execute("""
        CREATE TABLE IF NOT EXISTS notes.notes (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     TEXT NOT NULL,
            title       TEXT NOT NULL,
            body_md     TEXT NOT NULL,
            body_html   TEXT,
            tags        TEXT[] NOT NULL DEFAULT '{}',
            embedding   vector(1536),
            metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
            fts         TSVECTOR GENERATED ALWAYS AS (
                            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_md, ''))
                        ) STORED,
            deleted_at  TIMESTAMPTZ,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Create notes.links table
    op.execute("""
        CREATE TABLE IF NOT EXISTS notes.links (
            id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_id  UUID NOT NULL REFERENCES notes.notes(id) ON DELETE CASCADE,
            target_id  UUID NOT NULL REFERENCES notes.notes(id) ON DELETE CASCADE,
            context    TEXT
        )
    """)

    # Indexes on notes.notes
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_notes_user_updated "
        "ON notes.notes (user_id, updated_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_notes_fts "
        "ON notes.notes USING GIN (fts)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_notes_tags "
        "ON notes.notes USING GIN (tags)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_notes_embedding "
        "ON notes.notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # Index on notes.links
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_links_source "
        "ON notes.links (source_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_links_target "
        "ON notes.links (target_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notes.links")
    op.execute("DROP TABLE IF EXISTS notes.notes")
    op.execute("DROP SCHEMA IF EXISTS notes")
