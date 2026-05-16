from __future__ import annotations

import os
from copy import deepcopy
from flask import Flask, jsonify, request

app = Flask(__name__)

_INITIAL_TASKS = [
    {
        "id": 1,
        "title": "Implementar Hello World Flask",
        "description": "Criar a primeira rota da aplicação Flask.",
        "done": True,
    },
    {
        "id": 2,
        "title": "Transformar em API RESTful",
        "description": "Criar endpoints GET, POST, PUT e DELETE.",
        "done": False,
    },
]

tasks = deepcopy(_INITIAL_TASKS)
next_id = 3


@app.get("/")
def hello_world():
    return jsonify(
        {
            "message": "Hello World - Flask",
            "description": "Exercicio 9.1 - API Flask funcionando.",
            "endpoints": {
                "health": "/api/health",
                "tasks": "/api/tasks",
            },
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "framework": "Flask", "exercise": "9.1"}), 200


@app.get("/api/tasks")
def list_tasks():
    return jsonify(tasks), 200


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return jsonify({"error": "Tarefa nao encontrada"}), 404

    return jsonify(task), 200


@app.post("/api/tasks")
def create_task():
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title or not str(title).strip():
        return jsonify({"error": "Campo obrigatorio: title"}), 400

    task = {
        "id": next_id,
        "title": str(title).strip(),
        "description": str(data.get("description", "")).strip(),
        "done": bool(data.get("done", False)),
    }

    tasks.append(task)
    next_id += 1

    return jsonify(task), 201


@app.put("/api/tasks/<int:task_id>")
def update_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return jsonify({"error": "Tarefa nao encontrada"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        if not data["title"] or not str(data["title"]).strip():
            return jsonify({"error": "title nao pode ser vazio"}), 400
        task["title"] = str(data["title"]).strip()

    if "description" in data:
        task["description"] = str(data["description"]).strip()

    if "done" in data:
        task["done"] = bool(data["done"])

    return jsonify(task), 200


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        return jsonify({"error": "Tarefa nao encontrada"}), 404

    tasks.remove(task)

    return jsonify({"message": "Tarefa removida com sucesso"}), 200


def find_task(task_id: int) -> dict | None:
    return next((task for task in tasks if task["id"] == task_id), None)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
