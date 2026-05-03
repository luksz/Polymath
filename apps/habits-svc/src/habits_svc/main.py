from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from polymath_core.errors import PolymathError
from polymath_core.logging import configure_logging
from polymath_core.middleware import RequestIDMiddleware
from polymath_core.otel import configure_otel

from .api.v1.routes_habits import habits_router, todos_router
from .config import HabitsSvcSettings

settings = HabitsSvcSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)
    yield


app = FastAPI(
    title="Polymath Habits Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(habits_router)
app.include_router(todos_router)


@app.exception_handler(PolymathError)
async def polymath_error_handler(request: Request, exc: PolymathError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(request_id=request_id),
        media_type="application/problem+json",
    )


@app.get("/healthz", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def readiness() -> dict[str, str]:
    from .deps import get_settings
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()
    return {"status": "ok", "db": "ok"}


@app.get("/version", tags=["health"])
async def version() -> dict[str, str]:
    return {"service": "habits-svc", "version": "0.1.0"}
