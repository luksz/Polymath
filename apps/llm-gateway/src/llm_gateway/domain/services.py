from polymath_core.errors import BudgetExceededError
from polymath_llm.pricing import CostCalculator


class BudgetService:
    def __init__(self, cost_calc: CostCalculator) -> None:
        self._cost_calc = cost_calc

    def check_budget(
        self,
        model: str,
        input_tokens: int,
        max_tokens: int,
        spent_today: int,
        daily_limit: int,
        spent_month: int,
        monthly_limit: int,
    ) -> None:
        """Raise BudgetExceededError if estimated cost would breach a limit."""
        estimated = self._cost_calc.estimate(model, input_tokens, max_tokens)
        if spent_today + estimated > daily_limit:
            raise BudgetExceededError(
                f"Daily budget of ${daily_limit / 1_000_000:.2f} would be exceeded. "
                f"Spent today: ${spent_today / 1_000_000:.2f}"
            )
        if spent_month + estimated > monthly_limit:
            raise BudgetExceededError(
                f"Monthly budget of ${monthly_limit / 1_000_000:.2f} would be exceeded."
            )
