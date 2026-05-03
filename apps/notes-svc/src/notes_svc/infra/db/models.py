import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, DateTime, ForeignKey, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymath_db.base import Base


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "notes"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=text("'{}'"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    outbound_links: Mapped[list["NoteLink"]] = relationship(
        "NoteLink",
        foreign_keys="NoteLink.source_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    inbound_links: Mapped[list["NoteLink"]] = relationship(
        "NoteLink",
        foreign_keys="NoteLink.target_id",
        back_populates="target",
    )


class NoteLink(Base):
    __tablename__ = "links"
    __table_args__ = {"schema": "notes"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    context: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped["Note"] = relationship(
        "Note", foreign_keys=[source_id], back_populates="outbound_links"
    )
    target: Mapped["Note"] = relationship(
        "Note", foreign_keys=[target_id], back_populates="inbound_links"
    )
