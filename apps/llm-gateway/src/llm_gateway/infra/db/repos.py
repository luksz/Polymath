import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import LLMBudget, LLMPrompt, LLMPromptVersion, LLMRun


class RunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_run(
        self,
        user_id: str | None,
        model: str,
        provider: str,
        input: dict[str, Any],
        output: dict[str, Any] | None,
        input_tokens: int,
        output_tokens: int,
        cost_micro_usd: int,
        latency_ms: int,
        status: str,
        cache_hit: bool,
        prompt_version_id: uuid.UUID | None = None,
        error: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        run = LLMRun(
            user_id=uuid.UUID(user_id) if user_id else None,
            prompt_version_id=prompt_version_id,
            model=model,
            provider=provider,
            input=input,
            output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_micro_usd=cost_micro_usd,
            latency_ms=latency_ms,
            status=status,
            cache_hit=cache_hit,
            error=error,
        )
        self._session.add(run)
        await self._session.flush()
        return run.id


class PromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_prompts(self) -> list[LLMPrompt]:
        result = await self._session.execute(
            select(LLMPrompt).order_by(LLMPrompt.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_prompt_by_slug(self, slug: str) -> LLMPrompt | None:
        result = await self._session.execute(
            select(LLMPrompt).where(LLMPrompt.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create_prompt(
        self, slug: str, description: str | None = None
    ) -> LLMPrompt:
        prompt = LLMPrompt(slug=slug, description=description)
        self._session.add(prompt)
        await self._session.flush()
        return prompt

    async def create_version(
        self,
        prompt_id: uuid.UUID,
        template: str,
        variables: dict[str, Any],
        default_model: str,
        default_params: dict[str, Any],
        notes: str | None = None,
    ) -> LLMPromptVersion:
        result = await self._session.execute(
            select(func.coalesce(func.max(LLMPromptVersion.version), 0)).where(
                LLMPromptVersion.prompt_id == prompt_id
            )
        )
        next_version = (result.scalar() or 0) + 1
        pv = LLMPromptVersion(
            prompt_id=prompt_id,
            version=next_version,
            template=template,
            variables=variables,
            default_model=default_model,
            default_params=default_params,
            notes=notes,
        )
        self._session.add(pv)
        await self._session.flush()
        return pv

    async def get_version(self, slug: str, version: int) -> LLMPromptVersion | None:
        result = await self._session.execute(
            select(LLMPromptVersion)
            .join(LLMPrompt)
            .where(LLMPrompt.slug == slug, LLMPromptVersion.version == version)
        )
        return result.scalar_one_or_none()

    async def get_latest_version(self, slug: str) -> LLMPromptVersion | None:
        result = await self._session.execute(
            select(LLMPromptVersion)
            .join(LLMPrompt)
            .where(LLMPrompt.slug == slug)
            .order_by(LLMPromptVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class BudgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_budget(self, user_id: str | None) -> LLMBudget | None:
        if not user_id:
            return None
        result = await self._session.execute(
            select(LLMBudget).where(LLMBudget.user_id == uuid.UUID(user_id))
        )
        return result.scalar_one_or_none()

    async def get_or_create_budget(self, user_id: str) -> LLMBudget:
        budget = await self.get_budget(user_id)
        if budget:
            return budget
        from llm_gateway.config import LLMGatewaySettings

        s = LLMGatewaySettings()
        budget = LLMBudget(
            user_id=uuid.UUID(user_id),
            daily_limit_micro_usd=s.default_daily_limit_micro_usd,
            monthly_limit_micro_usd=s.default_monthly_limit_micro_usd,
        )
        self._session.add(budget)
        await self._session.flush()
        return budget


class UsageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_today_usage(self, user_id: str | None) -> dict[str, int]:
        today = date.today()
        query = select(
            func.count(LLMRun.id).label("run_count"),
            func.coalesce(func.sum(LLMRun.input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(LLMRun.output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(LLMRun.cost_micro_usd), 0).label("cost"),
        ).where(func.date(LLMRun.created_at) == today)
        if user_id:
            query = query.where(LLMRun.user_id == uuid.UUID(user_id))
        result = await self._session.execute(query)
        row = result.one()
        return {
            "run_count": row.run_count,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "cost": row.cost,
        }

    async def get_month_usage(self, user_id: str | None) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        query = select(
            func.count(LLMRun.id).label("run_count"),
            func.coalesce(func.sum(LLMRun.cost_micro_usd), 0).label("cost"),
        ).where(
            func.extract("year", LLMRun.created_at) == now.year,
            func.extract("month", LLMRun.created_at) == now.month,
        )
        if user_id:
            query = query.where(LLMRun.user_id == uuid.UUID(user_id))
        result = await self._session.execute(query)
        row = result.one()
        return {"run_count": row.run_count, "cost": row.cost}
