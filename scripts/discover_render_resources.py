#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE_URL = "https://api.render.com/v1"
EXPECTED_SERVICES = {
    "lab09-ex91-flask-api": "RENDER_SERVICE_ID_EX91_FLASK",
    "lab09-ex92-fastapi-api": "RENDER_SERVICE_ID_EX92_FASTAPI",
    "lab09-ex93-flask-hello": "RENDER_SERVICE_ID_EX93_HELLO_FLASK",
    "lab09-ex94-flask-restful": "RENDER_SERVICE_ID_EX94_FLASK_RESTFUL",
}


def request_json(path: str, api_key: str) -> Any:
    req = urllib.request.Request(
        f"{API_BASE_URL}{path}",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Render API HTTP {exc.code} em {path}: {body}") from exc


def walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_dicts(item)


def first_str(obj: dict, keys: list[str]) -> str | None:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def extract_blueprints(data: Any) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for obj in walk_dicts(data):
        blueprint_id = first_str(obj, ["id", "blueprintId"])
        if not blueprint_id:
            continue
        if not (blueprint_id.startswith("bpr-") or blueprint_id.startswith("bp-") or "blueprint" in blueprint_id):
            if not any(k in obj for k in ["autoSync", "path", "lastSync"]):
                continue
        name = first_str(obj, ["name", "repo", "path"]) or "Blueprint"
        path = first_str(obj, ["path", "blueprintPath"]) or ""
        repo = first_str(obj, ["repo", "repoURL", "repository", "nameWithOwner"]) or ""
        found[blueprint_id] = {"id": blueprint_id, "name": name, "path": path, "repo": repo}
    return list(found.values())


def extract_services(data: Any) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for obj in walk_dicts(data):
        service_id = first_str(obj, ["id", "serviceId"])
        if not service_id or not service_id.startswith("srv-"):
            continue
        name = first_str(obj, ["name", "serviceName"]) or ""
        if not name:
            continue
        url = first_str(obj, ["url", "serviceUrl", "dashboardUrl"]) or ""
        slug = first_str(obj, ["slug"]) or ""
        found[service_id] = {"id": service_id, "name": name, "url": url, "slug": slug}
    return list(found.values())


def save_env(path: str, blueprints: list[dict[str, str]], services: list[dict[str, str]]) -> None:
    lines = ["# Gerado por scripts/discover_render_resources.py"]

    if blueprints:
        lines.append(f"RENDER_BLUEPRINT_ID={blueprints[0]['id']}")

    for expected_name, secret_name in EXPECTED_SERVICES.items():
        match = next((svc for svc in services if svc["name"] == expected_name), None)
        if match:
            lines.append(f"{secret_name}={match['id']}")
            if match.get("url"):
                lines.append(f"{secret_name}_URL={match['url']}")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_services(services: list[dict[str, str]]) -> None:
    print("\nServiços encontrados:")
    if not services:
        print("  Nenhum serviço encontrado ainda.")
        return
    for svc in services:
        mark = "*" if svc["name"] in EXPECTED_SERVICES else "-"
        url = f" | URL: {svc['url']}" if svc.get("url") else ""
        print(f"  {mark} {svc['name']} | ID: {svc['id']}{url}")


def print_blueprints(blueprints: list[dict[str, str]]) -> None:
    print("\nBlueprints encontrados:")
    if not blueprints:
        print("  Nenhum Blueprint encontrado ainda.")
        return
    for bp in blueprints:
        details = []
        if bp.get("repo"):
            details.append(f"repo: {bp['repo']}")
        if bp.get("path"):
            details.append(f"path: {bp['path']}")
        suffix = " | " + " | ".join(details) if details else ""
        print(f"  - {bp['name']} | ID: {bp['id']}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.getenv("RENDER_API_KEY"), required=False)
    parser.add_argument("--owner-id", default=os.getenv("RENDER_OWNER_ID"), required=False)
    parser.add_argument("--repo-slug", default="")
    parser.add_argument("--out", default=".render/render_resources.env")
    parser.add_argument("--attempts", type=int, default=18)
    parser.add_argument("--sleep", type=int, default=10)
    args = parser.parse_args()

    if not args.api_key:
        print("Erro: informe --api-key ou RENDER_API_KEY", file=sys.stderr)
        return 1
    if not args.owner_id:
        print("Erro: informe --owner-id ou RENDER_OWNER_ID", file=sys.stderr)
        return 1

    query = urllib.parse.urlencode({"ownerId": args.owner_id, "limit": "100"})

    latest_blueprints: list[dict[str, str]] = []
    latest_services: list[dict[str, str]] = []

    for attempt in range(1, args.attempts + 1):
        print(f"\n[Busca {attempt}/{args.attempts}] Consultando Render API...")

        blueprints_raw = request_json(f"/blueprints?{query}", args.api_key)
        services_raw = request_json("/services?limit=100", args.api_key)

        Path(".render/render_blueprints_last.json").write_text(json.dumps(blueprints_raw, indent=2), encoding="utf-8")
        Path(".render/render_services_last.json").write_text(json.dumps(services_raw, indent=2), encoding="utf-8")

        latest_blueprints = extract_blueprints(blueprints_raw)
        latest_services = extract_services(services_raw)

        print_blueprints(latest_blueprints)
        print_services(latest_services)

        expected_count = sum(1 for svc in latest_services if svc["name"] in EXPECTED_SERVICES)
        if latest_blueprints and expected_count >= 4:
            print("\n[OK] Blueprint e os 4 serviços esperados foram encontrados.")
            break

        print(f"Ainda não encontrei tudo. Aguardando {args.sleep}s...")
        time.sleep(args.sleep)

    save_env(args.out, latest_blueprints, latest_services)
    print(f"\nArquivo de recursos salvo em: {args.out}")

    if not latest_blueprints:
        print("\nAviso: não encontrei o Blueprint. Se você ainda não clicou em Deploy Blueprint no Dashboard, faça isso e rode novamente:")
        print("  ./scripts/status_render_blueprint.sh")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
