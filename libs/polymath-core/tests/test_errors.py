import pytest

from polymath_core.errors import (
    BudgetExceededError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PolymathError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
)


def test_not_found_status_code():
    err = NotFoundError("item not found")
    assert err.status_code == 404


def test_to_dict_has_all_rfc7807_fields():
    err = NotFoundError("note 'abc' not found", instance="/v1/notes/abc")
    d = err.to_dict(request_id="req-123")
    assert d["type"].startswith("https://polymath.dev/errors/")
    assert d["title"] == "Resource not found"
    assert d["status"] == 404
    assert d["detail"] == "note 'abc' not found"
    assert d["instance"] == "/v1/notes/abc"
    assert d["request_id"] == "req-123"


def test_polymath_error_detail_in_dict():
    err = PolymathError("something broke")
    assert err.to_dict()["detail"] == "something broke"


def test_budget_exceeded_status():
    err = BudgetExceededError("daily budget exceeded")
    assert err.status_code == 429


@pytest.mark.parametrize(
    "error_cls,expected_status",
    [
        (NotFoundError, 404),
        (ValidationError, 422),
        (UnauthorizedError, 401),
        (ForbiddenError, 403),
        (ConflictError, 409),
        (RateLimitError, 429),
        (BudgetExceededError, 429),
    ],
)
def test_error_status_codes(error_cls, expected_status):
    err = error_cls("test")
    assert err.status_code == expected_status


def test_extra_kwargs_in_dict():
    err = NotFoundError("not found", instance="/v1/foo", field="id")
    d = err.to_dict()
    assert d["field"] == "id"
