from typing import Any


class PolymathError(Exception):
    """Base error for all Polymath services. Serialises to RFC 7807 problem+json."""

    status_code: int = 500
    error_type: str = "internal-error"
    title: str = "Internal server error"

    def __init__(self, detail: str, instance: str = "", **extra: Any) -> None:
        super().__init__(detail)
        self.detail = detail
        self.instance = instance
        self.extra = extra

    def to_dict(self, request_id: str = "") -> dict[str, Any]:
        return {
            "type": f"https://polymath.dev/errors/{self.error_type}",
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
            "instance": self.instance,
            "request_id": request_id,
            **self.extra,
        }


class NotFoundError(PolymathError):
    status_code = 404
    error_type = "not-found"
    title = "Resource not found"


class ValidationError(PolymathError):
    status_code = 422
    error_type = "validation-error"
    title = "Validation error"


class UnauthorizedError(PolymathError):
    status_code = 401
    error_type = "unauthorized"
    title = "Authentication required"


class ForbiddenError(PolymathError):
    status_code = 403
    error_type = "forbidden"
    title = "Access forbidden"


class ConflictError(PolymathError):
    status_code = 409
    error_type = "conflict"
    title = "Resource conflict"


class RateLimitError(PolymathError):
    status_code = 429
    error_type = "rate-limit-exceeded"
    title = "Rate limit exceeded"


class BudgetExceededError(PolymathError):
    status_code = 429
    error_type = "budget-exceeded"
    title = "Spending budget exceeded"
