#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_green()  { echo -e "${GREEN}✓ $1${NC}"; }
print_yellow() { echo -e "${YELLOW}→ $1${NC}"; }
print_red()    { echo -e "${RED}✗ $1${NC}"; }

echo ""
echo "========================================="
echo "  Polymath — Bootstrap"
echo "========================================="
echo ""

# Check prerequisites
print_yellow "Checking prerequisites..."

if ! command -v uv &>/dev/null; then
  print_red "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
print_green "uv $(uv --version)"

if ! command -v pnpm &>/dev/null; then
  print_red "pnpm not found. Install with: npm install -g pnpm"
  exit 1
fi
print_green "pnpm $(pnpm --version)"

if ! command -v docker &>/dev/null; then
  print_red "docker not found. Install Docker Desktop: https://www.docker.com"
  exit 1
fi
print_green "docker $(docker --version | cut -d' ' -f3 | tr -d ',')"

echo ""
print_yellow "Installing Python dependencies..."
uv sync --all-packages
print_green "Python deps installed"

echo ""
if [ -d "apps/web" ]; then
  print_yellow "Installing frontend dependencies..."
  (cd apps/web && pnpm install)
  print_green "Frontend deps installed"
else
  print_yellow "apps/web not found, skipping frontend deps"
fi

echo ""
print_yellow "Copying .env.example → .env (if not exists)..."
cp -n .env.example .env || true
print_green ".env ready"

echo ""
print_yellow "Starting Postgres, Redis, MinIO..."
docker compose up -d postgres redis minio
echo "Waiting for services to be healthy..."
sleep 4

print_yellow "Initialising MinIO bucket..."
docker compose up minio-init
print_green "MinIO bucket ready"

echo ""
echo "========================================="
print_green "Bootstrap complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: make dev"
echo "  3. Run: make test"
echo "========================================="
echo ""
