#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-}"
if [ -z "$NAME" ]; then
  echo "Usage: $0 <service-name>"
  echo "Example: $0 notes-svc"
  exit 1
fi

# Derive Python package name: replace hyphens with underscores
PKG="${NAME//-/_}"
DIR="apps/${NAME}"

if [ -d "$DIR" ]; then
  echo "Error: $DIR already exists."
  exit 1
fi

echo "Scaffolding service '${NAME}' → ${DIR}/"

mkdir -p "${DIR}/src/${PKG}/api/v1"
mkdir -p "${DIR}/src/${PKG}/domain"
mkdir -p "${DIR}/src/${PKG}/infra/db"
mkdir -p "${DIR}/src/${PKG}/workers"
mkdir -p "${DIR}/alembic/versions"
mkdir -p "${DIR}/tests/unit"
mkdir -p "${DIR}/tests/integration"

# pyproject.toml
cat > "${DIR}/pyproject.toml" << TOML
[project]
name = "${NAME}"
version = "0.1.0"
description = "Polymath ${NAME} service"
requires-python = ">=3.12"
dependencies = [
    "polymath-core",
    "polymath-db",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "redis[asyncio]>=5.0",
    "pydantic-settings>=2.2",
    "structlog>=24.1",
    "prometheus-fastapi-instrumentator>=7.0",
    "opentelemetry-instrumentation-fastapi>=0.45b0",
    "httpx>=0.27",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
TOML

# Dockerfile
cat > "${DIR}/Dockerfile" << 'DOCKER'
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install uv
COPY pyproject.toml .
COPY src/ src/
RUN uv pip install --system .

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /build/src /app/src
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "SERVICE_PKG.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKER
# Replace placeholder
sed -i.bak "s/SERVICE_PKG/${PKG}/g" "${DIR}/Dockerfile" && rm "${DIR}/Dockerfile.bak"

# alembic.ini
cat > "${DIR}/alembic.ini" << INI
[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s
truncate_slug_length = 40
timezone = UTC
INI

# alembic/env.py
cat > "${DIR}/alembic/env.py" << PYEOF
import asyncio
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://polymath:polymath@localhost:5432/polymath",
)

target_metadata = None  # replace with Base.metadata after defining models


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())
PYEOF

touch "${DIR}/alembic/versions/.gitkeep"

# Source files
touch "${DIR}/src/${PKG}/__init__.py"
touch "${DIR}/src/${PKG}/api/__init__.py"
touch "${DIR}/src/${PKG}/api/v1/__init__.py"
touch "${DIR}/src/${PKG}/domain/__init__.py"
touch "${DIR}/src/${PKG}/infra/__init__.py"
touch "${DIR}/src/${PKG}/infra/db/__init__.py"
touch "${DIR}/src/${PKG}/workers/__init__.py"

# config.py
cat > "${DIR}/src/${PKG}/config.py" << PYEOF
from polymath_core.config import Settings as BaseSettings


class Settings(BaseSettings):
    service_name: str = "${NAME}"
PYEOF

# main.py
cat > "${DIR}/src/${PKG}/main.py" << PYEOF
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from polymath_core.logging import configure_logging
from polymath_core.otel import configure_otel
from polymath_core.middleware import RequestIDMiddleware
from .config import Settings
from .api.health import health_router

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)
    yield


app = FastAPI(title="${NAME}", version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(health_router)


@app.get("/version")
async def version():
    return {"service": "${NAME}", "version": "0.1.0"}
PYEOF

# api/health.py
cat > "${DIR}/src/${PKG}/api/health.py" << PYEOF
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

health_router = APIRouter(tags=["health"])


@health_router.get("/healthz")
async def liveness():
    return {"status": "ok"}


@health_router.get("/readyz")
async def readiness():
    return {"status": "ok"}
PYEOF

# tests
touch "${DIR}/tests/__init__.py"
touch "${DIR}/tests/unit/__init__.py"
touch "${DIR}/tests/integration/__init__.py"

cat > "${DIR}/tests/conftest.py" << PYEOF
import pytest
from fastapi.testclient import TestClient
from ${PKG}.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
PYEOF

cat > "${DIR}/tests/unit/test_health.py" << PYEOF
def test_liveness(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
PYEOF

# README
cat > "${DIR}/README.md" << MDEOF
# ${NAME}

Polymath ${NAME} service.

## Run locally

\`\`\`bash
cd apps/${NAME}
uv run uvicorn ${PKG}.main:app --reload --port 8000
\`\`\`

## Endpoints

- \`GET /healthz\` — liveness
- \`GET /readyz\` — readiness
- \`GET /metrics\` — Prometheus metrics
- \`GET /version\` — service version
- \`GET /openapi.json\` — OpenAPI spec

## Configuration

See \`.env.example\` at repo root. All env vars are loaded via \`polymath_core.config.Settings\`.
MDEOF

echo ""
echo "✓ Service '${NAME}' scaffolded at ${DIR}/"
echo ""
echo "Next steps:"
echo "  1. Add '\"apps/${NAME}\"' to pyproject.toml workspace members"
echo "  2. Add the service to docker-compose.yml"
echo "  3. Run: make test"
