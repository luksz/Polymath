"""Initial content schema: posts and reading_log tables.

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
    op.execute("CREATE SCHEMA IF NOT EXISTS content")

    op.create_table(
        "posts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("slug", sa.Text, nullable=False, unique=True),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("body_mdx", sa.Text, nullable=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("cover_image_url", sa.Text, nullable=True),
        sa.Column("reading_minutes", sa.Integer, nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema="content",
    )

    op.create_index(
        "ix_posts_status_published_at",
        "posts",
        [sa.text("status"), sa.text("published_at DESC")],
        schema="content",
    )

    op.create_table(
        "reading_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("source", sa.Text, nullable=True),
        sa.Column("finished_on", sa.Date, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("notes_md", sa.Text, nullable=True),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.Text),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema="content",
    )


def downgrade() -> None:
    op.drop_table("reading_log", schema="content")
    op.drop_index("ix_posts_status_published_at", table_name="posts", schema="content")
    op.drop_table("posts", schema="content")
    op.execute("DROP SCHEMA IF EXISTS content")
