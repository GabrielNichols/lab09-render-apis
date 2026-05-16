#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def print_owners(data: Any) -> None:
    print("\nWorkspaces/owners encontrados:")
    if not isinstance(data, list):
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    for idx, item in enumerate(data, start=1):
        owner = item.get("owner", item) if isinstance(item, dict) else {}
        name = owner.get("name") or owner.get("email") or owner.get("slug") or "workspace"
        owner_id = owner.get("id") or item.get("id")
        print(f"  {idx}. {name} | ID: {owner_id}")


def print_validate(data: Any) -> None:
    print("\nResultado da validação do Blueprint:")

    valid = data.get("valid") if isinstance(data, dict) else None
    if valid is not None:
        print(f"  valid: {valid}")

    errors = data.get("errors") if isinstance(data, dict) else None
    warnings = data.get("warnings") if isinstance(data, dict) else None

    if errors:
        print("\nErros:")
        print(json.dumps(errors, indent=2, ensure_ascii=False))

    if warnings:
        print("\nAvisos:")
        print(json.dumps(warnings, indent=2, ensure_ascii=False))

    possible_plan = None
    if isinstance(data, dict):
        for key in ("plan", "changes", "resources", "services"):
            if key in data:
                possible_plan = data[key]
                break

    if possible_plan is not None:
        print("\nResumo do plano/recursos:")
        print(json.dumps(possible_plan, indent=2, ensure_ascii=False)[:4000])
    else:
        print("\nResposta resumida:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:4000])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    parser.add_argument("--kind", choices=["owners", "validate", "generic"], default="generic")
    args = parser.parse_args()

    data = load_json(args.json_file)

    if args.kind == "owners":
        print_owners(data)
    elif args.kind == "validate":
        print_validate(data)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
