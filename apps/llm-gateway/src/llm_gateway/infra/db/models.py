import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LLMPrompt(Base):
    __tablename__ = "prompts"
    __table_args__ = {"schema": "llm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    versions: Mapped[list["LLMPromptVersion"]] = relationship(
        back_populates="prompt", cascade="all, delete-orphan"
    )


class LLMPromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("prompt_id", "version"), {"schema": "llm"})

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("llm.prompts.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    default_model: Mapped[str] = mapped_column(Text, nullable=False)
    default_params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prompt: Mapped["LLMPrompt"] = relationship(back_populates="versions")


class LLMRun(Base):
    __tablename__ = "runs"
    __table_args__ = {"schema": "llm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm.prompt_versions.id")
    )
    model: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    input: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_micro_usd: Mapped[int | None] = mapped_column(BigInteger)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    trace_id: Mapped[str | None] = mapped_column(Text)
    cache_hit: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LLMEval(Base):
    __tablename__ = "evals"
    __table_args__ = {"schema": "llm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LLMEvalCase(Base):
    __tablename__ = "eval_cases"
    __table_args__ = {"schema": "llm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    eval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm.evals.id", ondelete="CASCADE"), nullable=False
    )
    input: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    expected: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    scorer: Mapped[str] = mapped_column(Text, nullable=False)
    scorer_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LLMEvalRun(Base):
    __tablename__ = "eval_runs"
    __table_args__ = {"schema": "llm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    eval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm.evals.id"), nullable=False
    )
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm.prompt_versions.id"), nullable=False
    )
    model: Mapped[str] = mapped_column(Text, nullable=False)
    pass_count: Mapped[int] = mapped_column(Integer, nullable=False)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_latency_ms: Mapped[int | None] = mapped_column(Integer)
    total_cost_micro_usd: Mapped[int | None] = mapped_column(BigInteger)
    results: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LLMBudget(Base):
    __tablename__ = "budgets"
    __table_args__ = {"schema": "llm"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    daily_limit_micro_usd: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default=text("5000000")
    )
    monthly_limit_micro_usd: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default=text("100000000")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
