SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTEST_ARGS ?=
SVC ?=
NAME ?=

.PHONY: help bootstrap dev dev-backend stop clean \
        test test-unit test-integration \
        lint format typecheck check \
        migrate gen-client new-service \
        logs psql redis-cli

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

bootstrap: ## First-time setup: install deps, start infra, copy .env
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || { echo "pnpm not found. Install: npm install -g pnpm"; exit 1; }
	uv sync --all-packages
	@if [ -d apps/web ]; then cd apps/web && pnpm install; fi
	cp -n .env.example .env || true
	docker compose up -d postgres redis minio
	@echo "Waiting for Postgres..." && sleep 3
	docker compose up minio-init
	@echo ""
	@echo "✓ Bootstrap complete. Run 'make dev' to start all services."

dev: ## Start all services via Docker Compose
	docker compose up

dev-backend: ## Start only Postgres, Redis, and MinIO
	docker compose up postgres redis minio

stop: ## Stop all Docker Compose services
	docker compose down

clean: ## Stop services, remove volumes, clean Python artifacts
	docker compose down -v --remove-orphans
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name 'dist' -not -path '*/node_modules/*' -exec rm -rf {} + 2>/dev/null; true

test: ## Run all tests
	uv run pytest $(PYTEST_ARGS)

test-unit: ## Run unit tests only
	uv run pytest -m unit $(PYTEST_ARGS)

test-integration: ## Run integration tests (requires running Postgres/Redis)
	uv run pytest -m integration $(PYTEST_ARGS)

lint: ## Run ruff linter
	uv run ruff check .

format: ## Auto-format with ruff
	uv run ruff format .

typecheck: ## Run mypy type checker
	uv run mypy apps/ libs/ --ignore-missing-imports

check: lint typecheck ## Run lint and typecheck

migrate: ## Run Alembic migrations for a service (usage: make migrate SVC=llm-gateway)
	@[ "$(SVC)" ] || { echo "Usage: make migrate SVC=<service-name>"; exit 1; }
	cd apps/$(SVC) && uv run alembic upgrade head

gen-client: ## Generate TypeScript API client from OpenAPI specs
	bash scripts/gen-client.sh

new-service: ## Scaffold a new backend service (usage: make new-service NAME=my-svc)
	@[ "$(NAME)" ] || { echo "Usage: make new-service NAME=<service-name>"; exit 1; }
	bash scripts/new-service.sh $(NAME)

logs: ## Tail logs for a service (usage: make logs SVC=postgres)
	docker compose logs -f $(SVC)

psql: ## Open psql in the running Postgres container
	docker compose exec postgres psql -U polymath polymath

redis-cli: ## Open redis-cli in the running Redis container
	docker compose exec redis redis-cli
