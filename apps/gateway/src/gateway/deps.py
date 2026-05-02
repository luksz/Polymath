from functools import lru_cache

from fastapi import Depends, Request
from polymath_core.errors import UnauthorizedError

from .auth import ClerkAuth
from .config import GatewaySettings


@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()


@lru_cache
def get_clerk_auth() -> ClerkAuth:
    settings = get_settings()
    return ClerkAuth(secret_key=settings.clerk_secret_key)


async def get_optional_user(
    request: Request,
    auth: ClerkAuth = Depends(get_clerk_auth),
) -> str | None:
    """Returns user_id or None. Does not raise for unauthenticated."""
    return await auth.verify_request(request)


async def require_user(
    user_id: str | None = Depends(get_optional_user),
) -> str:
    """Returns user_id. Raises 401 if unauthenticated."""
    if not user_id:
        raise UnauthorizedError("Authentication required")
    return user_id
