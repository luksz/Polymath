from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from polymath_core.logging import configure_logging
from polymath_core.middleware import RequestIDMiddleware
from polymath_core.otel import configure_otel

from .api import router
from .api.health import health_router
from .config import LLMGatewaySettings

settings = LLMGatewaySettings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)
    yield


app = FastAPI(
    title="Polymath LLM Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(health_router)
app.include_router(router, prefix="/v1")


@app.get("/version")
async def version() -> dict[str, str]:
    return {"service": "llm-gateway", "version": "0.1.0"}
