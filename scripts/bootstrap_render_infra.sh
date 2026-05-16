#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf '\n[INFO] Este comando agora usa o fluxo correto por Render Blueprint.\n'
printf '[INFO] Chamando scripts/bootstrap_render_blueprint.sh...\n\n'
exec "$SCRIPT_DIR/bootstrap_render_blueprint.sh" "$@"
