"""Persistência de tarefas.

Se a URL do banco for vazia, opera em memória. Caso contrário, usa asyncpg
contra um Postgres real.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Task:
    id: int
    title: str
    created_at: datetime


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id         BIGSERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


class Store:
    """Dois modos: em memória (pool=None) ou Postgres (pool != None)."""

    def __init__(self) -> None:
        self._pool = None
        self._lock = asyncio.Lock()
        self._mem: list[Task] = []
        self._next_id = 1

    @classmethod
    async def create(cls, database_url: str) -> "Store":
        store = cls()
        if not database_url:
            return store

        # Import tardio: assim os testes em memória não exigem asyncpg disponível.
        import asyncpg  # type: ignore

        pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
        async with pool.acquire() as conn:
            await conn.execute(SCHEMA)
        store._pool = pool
        return store

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()  # type: ignore[attr-defined]

    async def ping(self) -> bool:
        if self._pool is None:
            return True
        try:
            async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def list_tasks(self) -> list[Task]:
        if self._pool is None:
            async with self._lock:
                return list(self._mem)

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(
                "SELECT id, title, created_at FROM tasks ORDER BY id"
            )
        return [Task(id=r["id"], title=r["title"], created_at=r["created_at"]) for r in rows]

    async def create_task(self, title: str) -> Task:
        if not title:
            raise ValueError("title is required")

        if self._pool is None:
            async with self._lock:
                task = Task(
                    id=self._next_id,
                    title=title,
                    created_at=datetime.now(timezone.utc),
                )
                self._next_id += 1
                self._mem.append(task)
                return task

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(
                "INSERT INTO tasks (title) VALUES ($1) RETURNING id, title, created_at",
                title,
            )
        return Task(id=row["id"], title=row["title"], created_at=row["created_at"])
