from __future__ import annotations

import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Lab 09 - API RESTful com FastAPI",
    description="Exercicio 9.2 - API de tarefas usando FastAPI e Uvicorn.",
    version="1.0.0",
)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, examples=["Estudar FastAPI"])
    description: Optional[str] = Field(default="", examples=["Criar endpoints RESTful"])
    done: bool = Field(default=False)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    done: Optional[bool] = None


class Task(TaskCreate):
    id: int


tasks: list[Task] = [
    Task(id=1, title="Implementar API FastAPI", description="Criar rotas RESTful.", done=True),
    Task(id=2, title="Testar no Postman", description="Validar GET, POST, PUT e DELETE.", done=False),
]
next_id = 3


@app.get("/")
def index():
    return {
        "message": "API RESTful FastAPI funcionando!",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "tasks": "/api/tasks",
        },
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "framework": "FastAPI", "exercise": "9.2"}


@app.get("/api/tasks", response_model=list[Task])
def list_tasks():
    return tasks


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada")

    return task


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global next_id

    task = Task(
        id=next_id,
        title=payload.title.strip(),
        description=(payload.description or "").strip(),
        done=payload.done,
    )

    tasks.append(task)
    next_id += 1

    return task


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada")

    if payload.title is not None:
        task.title = payload.title.strip()

    if payload.description is not None:
        task.description = payload.description.strip()

    if payload.done is not None:
        task.done = payload.done

    return task


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada")

    tasks.remove(task)

    return {"message": "Tarefa removida com sucesso"}


def find_task(task_id: int) -> Task | None:
    return next((task for task in tasks if task.id == task_id), None)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
