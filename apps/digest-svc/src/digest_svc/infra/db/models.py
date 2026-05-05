import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Date, DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from polymath_db.base import Base


class Digest(Base):
    __tablename__ = "digests"
    __table_args__ = {"schema": "digest"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    for_date: Mapped[object] = mapped_column(Date, nullable=False, unique=True)
    topic_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'pending'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    papers: Mapped[list["DigestPaper"]] = relationship(
        "DigestPaper",
        back_populates="digest",
        cascade="all, delete-orphan",
    )


class DigestPaper(Base):
    __tablename__ = "papers"
    __table_args__ = {"schema": "digest"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    digest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("digest.digests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    arxiv_id: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    arxiv_url: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_headline: Mapped[str] = mapped_column(Text, nullable=False)
    summary_body: Mapped[str] = mapped_column(Text, nullable=False)
    key_insight: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    digest: Mapped["Digest"] = relationship("Digest", back_populates="papers")
