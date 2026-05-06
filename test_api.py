"""Testes de integração da API.

Usam o TestClient do FastAPI, que aciona o lifespan da aplicação. Como
não definimos DATABASE_URL no ambiente de teste, o store roda em memória.
"""
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["db"] == "ok"  # store em memória sempre responde


def test_create_and_list_tasks():
    with TestClient(app) as client:
        r = client.post("/tasks", json={"title": "escrever ci.yml"})
        assert r.status_code == 201
        created = r.json()
        assert created["id"] == 1
        assert created["title"] == "escrever ci.yml"

        r = client.get("/tasks")
        assert r.status_code == 200
        tasks = r.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "escrever ci.yml"


def test_create_task_validation_empty_title():
    with TestClient(app) as client:
        r = client.post("/tasks", json={"title": ""})
        # pydantic rejeita por min_length=1 → 422
        assert r.status_code == 422


def test_create_task_validation_missing_field():
    with TestClient(app) as client:
        r = client.post("/tasks", json={})
        assert r.status_code == 422
