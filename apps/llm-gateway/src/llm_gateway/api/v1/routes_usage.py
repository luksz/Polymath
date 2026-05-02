from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_db, get_user_id
from ...infra.db.repos import BudgetRepository, UsageRepository
from .schemas import UsageSummarySchema

router = APIRouter()


@router.get("", response_model=UsageSummarySchema)
async def get_usage(
    db: AsyncSession = Depends(get_db),
    user_id: str | None = Depends(get_user_id),
) -> UsageSummarySchema:
    usage_repo = UsageRepository(db)
    budget_repo = BudgetRepository(db)

    today = await usage_repo.get_today_usage(user_id)
    month = await usage_repo.get_month_usage(user_id)
    budget = await budget_repo.get_budget(user_id)

    return UsageSummarySchema(
        total_runs=today.get("run_count", 0),
        total_input_tokens=today.get("input_tokens", 0),
        total_output_tokens=today.get("output_tokens", 0),
        total_cost_micro_usd=today.get("cost", 0),
        budget_daily_micro_usd=budget.daily_limit_micro_usd if budget else 5_000_000,
        budget_monthly_micro_usd=budget.monthly_limit_micro_usd if budget else 100_000_000,
        spent_today_micro_usd=today.get("cost", 0),
        spent_this_month_micro_usd=month.get("cost", 0),
    )
