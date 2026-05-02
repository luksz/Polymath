from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db

health_router = APIRouter(tags=["health"])


@health_router.get("/healthz")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@health_router.get("/readyz")
async def readiness(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
