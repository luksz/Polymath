import pytest

from polymath_core.errors import BudgetExceededError
from polymath_llm.pricing import CostCalculator
from llm_gateway.domain.services import BudgetService


@pytest.fixture
def svc() -> BudgetService:
    return BudgetService(CostCalculator())


def test_within_budget_passes(svc):
    svc.check_budget(
        model="claude-haiku-4-5-20251001",
        input_tokens=100,
        max_tokens=100,
        spent_today=0,
        daily_limit=5_000_000,
        spent_month=0,
        monthly_limit=100_000_000,
    )


def test_daily_limit_exceeded_raises(svc):
    with pytest.raises(BudgetExceededError):
        svc.check_budget(
            model="claude-opus-4-7",
            input_tokens=100_000,
            max_tokens=100_000,
            spent_today=4_999_000,
            daily_limit=5_000_000,
            spent_month=0,
            monthly_limit=100_000_000,
        )


def test_monthly_limit_exceeded_raises(svc):
    with pytest.raises(BudgetExceededError):
        svc.check_budget(
            model="claude-sonnet-4-6",
            input_tokens=100_000,
            max_tokens=50_000,
            spent_today=0,
            daily_limit=5_000_000,
            spent_month=99_999_000,
            monthly_limit=100_000_000,
        )
