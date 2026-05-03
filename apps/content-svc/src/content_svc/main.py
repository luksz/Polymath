from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from polymath_core.errors import PolymathError
from polymath_core.logging import configure_logging
from polymath_core.middleware import RequestIDMiddleware
from polymath_core.otel import configure_otel

from .api.v1.routes_content import feeds_router, posts_router, reading_log_router
from .config import ContentSvcSettings
from .deps import get_db

settings = ContentSvcSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)
    yield


app = FastAPI(
    title="Polymath Content Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(posts_router)
app.include_router(reading_log_router)
app.include_router(feeds_router)


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
    async for db in get_db():
        await db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}


@app.get("/version", tags=["health"])
async def version() -> dict[str, str]:
    return {"service": "content-svc", "version": "0.1.0"}
