#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .render
LOG_FILE=".render/bootstrap_blueprint_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

log() {
  printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$1"
}

ok() {
  printf '[OK] %s\n' "$1"
}

warn() {
  printf '[WARN] %s\n' "$1"
}

fail() {
  printf '\n[ERRO] %s\n' "$1" >&2
  printf '[ERRO] Log salvo em: %s\n' "$LOG_FILE" >&2
  exit 1
}

trap 'fail "Falhou na linha ${LINENO}: ${BASH_COMMAND}"' ERR

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Comando obrigatório não encontrado: $1"
  ok "Encontrado: $1"
}

ask_required() {
  local var_name="$1"
  local prompt="$2"
  local current_value="${!var_name:-}"

  if [ -n "$current_value" ]; then
    ok "$var_name já definido no ambiente"
    return 0
  fi

  if [ ! -t 0 ]; then
    fail "$var_name não está definido e o terminal não é interativo. Rode: export $var_name='valor'"
  fi

  local value
  read -r -p "$prompt" value

  if [ -z "$value" ]; then
    fail "$var_name não pode ficar vazio"
  fi

  export "$var_name=$value"
}

api_get() {
  local path="$1"
  local out_file="$2"
  local code

  code=$(curl -sS -w '%{http_code}' -o "$out_file" \
    --request GET \
    --url "https://api.render.com/v1${path}" \
    --header "Authorization: Bearer ${RENDER_API_KEY}" \
    --header "Accept: application/json")

  if [ "$code" -lt 200 ] || [ "$code" -ge 300 ]; then
    cat "$out_file" || true
    fail "Render API GET ${path} retornou HTTP ${code}"
  fi
}

validate_blueprint() {
  local out_file=".render/blueprint_validate.json"
  local code

  log "Validando render.yaml pela API oficial do Render"

  code=$(curl -sS -w '%{http_code}' -o "$out_file" \
    --request POST \
    --url "https://api.render.com/v1/blueprints/validate" \
    --header "Authorization: Bearer ${RENDER_API_KEY}" \
    --header "Accept: application/json" \
    --form "ownerId=${RENDER_OWNER_ID}" \
    --form "file=@render.yaml")

  if [ "$code" -lt 200 ] || [ "$code" -ge 300 ]; then
    cat "$out_file" || true
    fail "Validação do Blueprint retornou HTTP ${code}"
  fi

  python3 scripts/render_json_summary.py "$out_file" --kind validate
  ok "render.yaml validado. Resposta completa salva em $out_file"
}

ensure_git_repo() {
  log "Conferindo repositório Git"

  if [ ! -d .git ]; then
    warn "Esta pasta ainda não era um repositório Git. Inicializando..."
    git init
    git branch -M main
  fi

  local gh_user
  gh_user="$(gh api user --jq .login 2>/dev/null || true)"
  gh_user="${gh_user:-github-user}"

  if ! git config user.name >/dev/null; then
    git config user.name "$gh_user"
    ok "git user.name configurado localmente: $gh_user"
  fi

  if ! git config user.email >/dev/null; then
    git config user.email "${gh_user}@users.noreply.github.com"
    ok "git user.email configurado localmente"
  fi

  if [ -z "$(git branch --show-current || true)" ]; then
    git checkout -b main
  fi
}

commit_and_push() {
  log "Commitando e enviando o projeto para o GitHub"

  git add .

  if git diff --cached --quiet; then
    ok "Nenhuma alteração nova para commitar"
  else
    git commit -m "Configure Render Blueprint deploy"
    ok "Commit criado"
  fi

  local branch
  branch="$(git branch --show-current)"

  if ! git remote get-url origin >/dev/null 2>&1; then
    local default_repo_name="lab09-render-blueprint"
    local repo_name

    if [ -t 0 ]; then
      read -r -p "Nome do novo repositório no GitHub [${default_repo_name}]: " repo_name
      repo_name="${repo_name:-$default_repo_name}"
    else
      repo_name="$default_repo_name"
    fi

    log "Criando repositório GitHub: ${repo_name}"
    gh repo create "$repo_name" --public --source=. --remote=origin --push
  else
    log "Remote origin encontrado: $(git remote get-url origin)"
    git push -u origin "$branch"
  fi

  REPO_URL="$(gh repo view --json url -q .url)"
  REPO_SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
  BRANCH="$branch"

  ok "Repo GitHub: $REPO_SLUG"
  ok "Branch: $BRANCH"
}

print_owners() {
  log "Buscando workspaces/owners no Render"
  api_get "/owners" ".render/render_owners.json"
  python3 scripts/render_json_summary.py ".render/render_owners.json" --kind owners
}

set_github_secrets() {
  log "Configurando secrets no GitHub Actions com gh cli"

  gh secret set RENDER_API_KEY -b "$RENDER_API_KEY"
  ok "Secret configurado: RENDER_API_KEY"

  gh secret set RENDER_OWNER_ID -b "$RENDER_OWNER_ID"
  ok "Secret configurado: RENDER_OWNER_ID"
}

wait_for_blueprint_and_discover() {
  if [ ! -t 0 ]; then
    warn "Terminal não interativo. Pulei a etapa de descoberta pós-deploy."
    return 0
  fi

  cat <<EOF

================================================================================
AÇÃO MANUAL ÚNICA NO RENDER
================================================================================
1. Abra o Render Dashboard.
2. Clique em New + > Blueprint.
3. Conecte este repositório:
   ${REPO_SLUG}
4. Use a branch:
   ${BRANCH}
5. Use o path do Blueprint:
   render.yaml
6. Revise o plano e clique em Deploy Blueprint.

Importante: depois dessa primeira criação, o Blueprint fica conectado ao repo.
A partir daí, pushes na branch disparam sincronização/deploy automaticamente.
================================================================================
EOF

  read -r -p "Depois de clicar em Deploy Blueprint no Render, pressione ENTER para eu procurar os recursos criados..."

  log "Procurando Blueprints e serviços criados no Render"
  python3 scripts/discover_render_resources.py \
    --api-key "$RENDER_API_KEY" \
    --owner-id "$RENDER_OWNER_ID" \
    --repo-slug "$REPO_SLUG" \
    --out ".render/render_resources.env"

  if [ -f .render/render_resources.env ]; then
    log "Publicando IDs encontrados como GitHub Actions secrets"
    while IFS='=' read -r key value; do
      [[ -z "${key:-}" || "$key" == \#* ]] && continue
      if [ -n "${value:-}" ]; then
        gh secret set "$key" -b "$value"
        ok "Secret configurado: $key"
      fi
    done < .render/render_resources.env
  fi
}

main() {
  log "Bootstrap Render Blueprint iniciado"
  ok "Diretório do projeto: $ROOT_DIR"
  ok "Log desta execução: $LOG_FILE"

  require_cmd git
  require_cmd gh
  require_cmd curl
  require_cmd python3

  if [ ! -f render.yaml ]; then
    fail "render.yaml não encontrado na raiz do projeto"
  fi

  log "Conferindo autenticação do GitHub CLI"
  gh auth status
  ok "GitHub CLI autenticado"

  ensure_git_repo

  ask_required RENDER_API_KEY "Cole sua Render API Key: "

  print_owners
  ask_required RENDER_OWNER_ID "Cole o owner/workspace ID do Render escolhido acima: "

  set_github_secrets
  validate_blueprint
  commit_and_push
  wait_for_blueprint_and_discover

  cat <<EOF

================================================================================
FINALIZADO
================================================================================
- Projeto enviado para o GitHub.
- render.yaml validado pela API do Render.
- Secrets configurados no GitHub Actions.
- Log completo: ${LOG_FILE}

Para acompanhar depois:
  ./scripts/status_render_blueprint.sh

Para testar localmente:
  ./scripts/test_local_all.sh
================================================================================
EOF
}

main "$@"
