from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from polymath_core.errors import PolymathError
from polymath_core.logging import configure_logging
from polymath_core.middleware import RequestIDMiddleware
from polymath_core.otel import configure_otel

from .api import router
from .api.v1.routes_health import health_router
from .config import GatewaySettings

settings = GatewaySettings()
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)
    yield


app = FastAPI(title="Polymath Gateway", version="0.1.0", lifespan=lifespan)

# Middleware (order matters — outermost runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://polymath.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Error handler — convert PolymathError to RFC 7807 JSON
@app.exception_handler(PolymathError)
async def polymath_error_handler(request: Request, exc: PolymathError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(request_id=request_id),
        media_type="application/problem+json",
    )


# Metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Routes
app.include_router(health_router)
app.include_router(router)


@app.get("/version")
async def version() -> dict:
    return {"service": "gateway", "version": "0.1.0"}
