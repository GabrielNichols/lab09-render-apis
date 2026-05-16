#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE_URL = "https://api.render.com/v1"
PYTHON_VERSION = "3.12.4"
REGION = "oregon"
PLAN = "free"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria os Web Services do Lab 09 no Render e gera arquivo .env com os IDs."
    )
    parser.add_argument("--api-key", default=os.getenv("RENDER_API_KEY"), help="Render API key")
    parser.add_argument("--owner-id", required=True, help="Workspace/owner ID do Render")
    parser.add_argument("--repo", required=True, help="URL do repositorio GitHub/GitLab/Bitbucket")
    parser.add_argument("--branch", default="main", help="Branch usada pelo Render")
    parser.add_argument("--prefix", default="", help="Prefixo opcional para evitar colisao de nomes")
    parser.add_argument("--config", default="scripts/services_config.json", help="Arquivo JSON de servicos")
    parser.add_argument("--out", default=".render/services.env", help="Arquivo de saida com secrets")
    parser.add_argument("--dry-run", action="store_true", help="Mostra payloads sem criar nada")
    return parser.parse_args()


def request_json(method: str, path: str, api_key: str, payload: dict | None = None) -> dict:
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(f"{API_BASE_URL}{path}", data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Render API error {error.code} em {path}: {body}") from error


def service_payload(service: dict, owner_id: str, repo: str, branch: str, prefix: str) -> dict:
    service_name = f"{prefix}-{service['name']}" if prefix else service["name"]

    return {
        "type": "web_service",
        "name": service_name,
        "ownerId": owner_id,
        "repo": repo,
        "branch": branch,
        "autoDeploy": "no",
        "rootDir": service["root_dir"],
        "envVars": [
            {"key": "PYTHON_VERSION", "value": PYTHON_VERSION},
        ],
        "serviceDetails": {
            "runtime": "python",
            "plan": PLAN,
            "region": REGION,
            "healthCheckPath": service["health_check_path"],
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": service["start_command"],
            },
        },
    }


def find_service_id(response: dict) -> str | None:
    candidates = []

    def walk(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == "id" and isinstance(v, str) and v.startswith("srv-"):
                    candidates.append(v)
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(response)
    return candidates[0] if candidates else None


def trigger_initial_deploy(api_key: str, service_id: str) -> None:
    try:
        request_json(
            "POST",
            f"/services/{service_id}/deploys",
            api_key,
            {"clearCache": "do_not_clear"},
        )
    except RuntimeError as error:
        print(f"Aviso: servico {service_id} criado, mas deploy inicial nao foi disparado: {error}", file=sys.stderr)


def main() -> int:
    args = parse_args()

    if not args.api_key:
        print("Erro: informe --api-key ou exporte RENDER_API_KEY.", file=sys.stderr)
        return 1

    config_path = Path(args.config)
    services = json.loads(config_path.read_text(encoding="utf-8"))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    env_lines = ["# Arquivo gerado automaticamente por scripts/create_render_services.py"]

    for service in services:
        payload = service_payload(service, args.owner_id, args.repo, args.branch, args.prefix)
        print(f"\n==> Criando servico Render: {payload['name']}")

        if args.dry_run:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            continue

        response = request_json("POST", "/services", args.api_key, payload)
        service_id = find_service_id(response)

        if not service_id:
            print(json.dumps(response, indent=2, ensure_ascii=False), file=sys.stderr)
            raise RuntimeError("Nao consegui localizar o service ID na resposta do Render.")

        print(f"Criado: {payload['name']} -> {service_id}")
        env_lines.append(f"{service['secret_name']}={service_id}")

        print("Disparando deploy inicial...")
        trigger_initial_deploy(args.api_key, service_id)
        time.sleep(1)

    if not args.dry_run:
        out_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        print(f"\nIDs salvos em: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
