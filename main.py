"""API de tarefas — base para a Sprint 2.

Se DATABASE_URL estiver definida, conecta no Postgres.
Caso contrário, usa um store em memória (útil para CI rápido e testes locais).
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.storage import Store


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = os.getenv("DATABASE_URL", "")
    store = await Store.create(database_url)
    app.state.store = store
    try:
        yield
    finally:
        await store.close()


app = FastAPI(title="Tasks API — Sprint 2 base", lifespan=lifespan)


def get_store(request: Request) -> Store:
    return request.app.state.store


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskOut(BaseModel):
    id: int
    title: str
    created_at: datetime


@app.get("/health")
async def health(request: Request):
    store = get_store(request)
    db_ok = await store.ping()
    payload = {"status": "ok", "db": "ok" if db_ok else "down"}
    if not db_ok:
        # 503 quando o banco está fora — útil para healthchecks de orquestradores
        raise HTTPException(status_code=503, detail=payload)
    return payload


@app.get("/tasks", response_model=list[TaskOut])
async def list_tasks(request: Request):
    store = get_store(request)
    return await store.list_tasks()


@app.post("/tasks", response_model=TaskOut, status_code=201)
async def create_task(payload: TaskIn, request: Request):
    store = get_store(request)
    return await store.create_task(payload.title)


# Permite "python -m app.main" rodar o servidor diretamente, sem fastapi-cli.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=False,
    )
