#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

command -v gh >/dev/null 2>&1 || { echo "Erro: instale o GitHub CLI: gh"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Erro: instale o Git"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Erro: instale Python 3"; exit 1; }

gh auth status >/dev/null || {
  echo "Voce ainda nao esta logado no GitHub CLI. Rode: gh auth login"
  exit 1
}

if [ -z "${RENDER_API_KEY:-}" ]; then
  read -rsp "Cole sua Render API Key: " RENDER_API_KEY
  echo ""
fi

if [ -z "${RENDER_OWNER_ID:-}" ]; then
  echo "Buscando workspaces no Render..."
  owners_json="$(curl -fsS \
    --url "https://api.render.com/v1/owners" \
    --header "Authorization: Bearer ${RENDER_API_KEY}" \
    --header "Accept: application/json")"

  python3 - <<'PY' <<<"$owners_json"
import json, sys
owners = json.load(sys.stdin)
for idx, item in enumerate(owners, start=1):
    owner = item.get("owner", item)
    print(f"{idx}. {owner.get('name') or owner.get('email') or 'workspace'} | {owner.get('id')}")
PY

  read -rp "Cole o owner/workspace ID escolhido: " RENDER_OWNER_ID
fi

REPO_URL="$(gh repo view --json url -q .url)"
BRANCH="$(git branch --show-current || true)"
BRANCH="${BRANCH:-main}"
SERVICE_PREFIX="${SERVICE_PREFIX:-}"

cat <<EOF

Config escolhida:
- Repo: ${REPO_URL}
- Branch: ${BRANCH}
- Render owner ID: ${RENDER_OWNER_ID}
- Prefixo: ${SERVICE_PREFIX:-sem prefixo}
EOF

read -rp "Continuar criando a infra no Render? [s/N] " confirm
case "$confirm" in
  s|S|sim|SIM) ;;
  *) echo "Cancelado."; exit 0 ;;
esac

# Salva os segredos-base no repositorio do GitHub.
gh secret set RENDER_API_KEY -b "$RENDER_API_KEY"
gh secret set RENDER_OWNER_ID -b "$RENDER_OWNER_ID"

# Cria os web services no Render e gera .render/services.env.
python3 scripts/create_render_services.py \
  --api-key "$RENDER_API_KEY" \
  --owner-id "$RENDER_OWNER_ID" \
  --repo "$REPO_URL" \
  --branch "$BRANCH" \
  ${SERVICE_PREFIX:+--prefix "$SERVICE_PREFIX"} \
  --out .render/services.env

# Publica automaticamente os IDs dos servicos como secrets do GitHub Actions.
while IFS='=' read -r key value; do
  [[ -z "${key:-}" || "$key" == \#* ]] && continue
  gh secret set "$key" -b "$value"
  echo "Secret configurado: $key"
done < .render/services.env

cat <<'EOF'

Pronto.
Agora rode:
  git add .
  git commit -m "Lab 09 Render CI/CD"
  git push origin main

O workflow CI - Tests vai rodar os testes.
Depois, o workflow CD - Deploy to Render vai disparar o deploy usando a API do Render.
EOF
