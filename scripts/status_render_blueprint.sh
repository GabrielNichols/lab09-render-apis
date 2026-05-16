#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p .render

log() { printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$1"; }

if [ -z "${RENDER_API_KEY:-}" ]; then
  read -r -p "Cole sua Render API Key: " RENDER_API_KEY
  export RENDER_API_KEY
fi

if [ -z "${RENDER_OWNER_ID:-}" ]; then
  read -r -p "Cole seu Render owner/workspace ID: " RENDER_OWNER_ID
  export RENDER_OWNER_ID
fi

REPO_SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"

log "Consultando status dos Blueprints e serviços no Render"
python3 scripts/discover_render_resources.py \
  --api-key "$RENDER_API_KEY" \
  --owner-id "$RENDER_OWNER_ID" \
  --repo-slug "$REPO_SLUG" \
  --out ".render/render_resources.env" \
  --attempts 1 \
  --sleep 1

log "Arquivos completos de resposta salvos em:"
printf '  - .render/render_blueprints_last.json\n'
printf '  - .render/render_services_last.json\n'
printf '  - .render/render_resources.env\n'
