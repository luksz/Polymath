#!/usr/bin/env bash
set -euo pipefail

SERVICES=(
  "gateway:8000"
  "llm-gateway:8001"
  "notes-svc:8002"
  "habits-svc:8003"
  "content-svc:8004"
  "analytics-svc:8005"
  "games-svc:8006"
)

OUT_DIR="apps/web/lib/api-client"
MERGE_INPUT="/tmp/polymath-openapi-merge.json"
MERGED_SPEC="/tmp/polymath-openapi.json"

if [ ! -d "apps/web" ]; then
  echo "apps/web not found. Create the Next.js app first."
  exit 1
fi

echo "Fetching OpenAPI specs from running services..."

FETCHED=()
MERGE_CONFIGS=()

for entry in "${SERVICES[@]}"; do
  svc="${entry%%:*}"
  port="${entry##*:}"
  url="http://localhost:${port}/openapi.json"

  if curl -sf "$url" -o "/tmp/openapi-${svc}.json" 2>/dev/null; then
    echo "  ✓ ${svc} (port ${port})"
    FETCHED+=("$svc")
    MERGE_CONFIGS+=("{\"inputFile\": \"/tmp/openapi-${svc}.json\", \"operationSelection\": {\"includeTags\": []}}")
  else
    echo "  ✗ ${svc} not running, skipping"
  fi
done

if [ ${#FETCHED[@]} -eq 0 ]; then
  echo "No services running. Start services with 'make dev' first."
  exit 1
fi

echo "Merging ${#FETCHED[@]} specs..."
MERGE_JSON="{\"inputs\": [$(IFS=,; echo "${MERGE_CONFIGS[*]}")]}"
echo "$MERGE_JSON" > "$MERGE_INPUT"
pnpm dlx openapi-merge-cli --config "$MERGE_INPUT" --output "$MERGED_SPEC"

echo "Generating TypeScript client..."
mkdir -p "$OUT_DIR"
pnpm dlx openapi-typescript "$MERGED_SPEC" -o "${OUT_DIR}/schema.d.ts"

echo ""
echo "✓ Client generated at ${OUT_DIR}/"
echo "  Import with: import type { paths } from '@/lib/api-client/schema'"
