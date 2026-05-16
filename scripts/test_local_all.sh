#!/usr/bin/env bash
set -euo pipefail

apps=(
  "exercicio_9_1_flask"
  "exercicio_9_2_fastapi"
  "exercicio_9_3_render_hello_flask"
  "exercicio_9_4_render_flask_restful"
)

for app in "${apps[@]}"; do
  echo "\n==> Testando $app"
  (cd "$app" && python -m pip install -q -r requirements.txt && pytest -q)
done
