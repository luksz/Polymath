import pytest

from polymath_llm.pricing import CostCalculator


@pytest.fixture
def calc() -> CostCalculator:
    return CostCalculator()


def test_known_model_returns_nonzero(calc):
    cost = calc.calculate("claude-sonnet-4-6", 1000, 500)
    assert cost > 0


def test_unknown_model_returns_zero(calc):
    cost = calc.calculate("unknown-model-xyz", 1000, 500)
    assert cost == 0


def test_estimate_returns_int(calc):
    estimate = calc.estimate("gpt-4o-mini", 500, 1000)
    assert isinstance(estimate, int)
    assert estimate > 0


def test_cost_is_integer_not_float(calc):
    cost = calc.calculate("claude-haiku-4-5-20251001", 999, 1)
    assert isinstance(cost, int)


def test_zero_tokens_zero_cost(calc):
    cost = calc.calculate("gpt-4o", 0, 0)
    assert cost == 0


def test_embedding_model_output_cost_is_zero(calc):
    cost_with_output = calc.calculate("text-embedding-3-small", 1000, 1000)
    cost_no_output = calc.calculate("text-embedding-3-small", 1000, 0)
    assert cost_with_output == cost_no_output
