from functools import lru_cache

from fastapi import Header, HTTPException
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from polymath_llm import LLMClient

from .config import LLMGatewaySettings

_engine = None
_session_factory = None
_redis_pool = None


@lru_cache
def get_settings() -> LLMGatewaySettings:
    return LLMGatewaySettings()


def _get_engine():  # type: ignore[no-untyped-def]
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(_get_engine(), expire_on_commit=False)
    return _session_factory


async def get_db() -> AsyncSession:  # type: ignore[misc]
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis() -> Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(get_settings().redis_url)
    return Redis(connection_pool=_redis_pool)


def get_llm_client() -> LLMClient:
    return LLMClient(redis=get_redis())


async def get_user_id(
    x_polymath_user_id: str | None = Header(default=None),
) -> str | None:
    return x_polymath_user_id
