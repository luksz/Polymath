from fastapi import APIRouter

health_router = APIRouter(tags=["health"])


@health_router.get("/healthz")
async def liveness() -> dict:
    return {"status": "ok"}


@health_router.get("/readyz")
async def readiness() -> dict:
    # Gateway has no DB; just check it's up
    return {"status": "ok"}
