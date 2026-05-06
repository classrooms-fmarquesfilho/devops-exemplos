# Sprint 2 — repositório base

API simples em Python (FastAPI + Postgres) que vamos transformar num pipeline DevOps na aula de hoje.

## Estrutura

```
.
├── app/
│   ├── main.py           # rotas e modelos da API
│   └── storage.py        # persistência (Postgres ou memória)
├── tests/
│   └── test_api.py
├── requirements.txt
├── requirements-dev.txt
├── STEP-1.md             # ← começar aqui
├── STEP-2.md
└── STEP-3.md
```

## A API

| Método | Rota | O que faz |
|---|---|---|
| GET | `/health` | Status da aplicação e do banco |
| GET | `/tasks` | Lista tarefas |
| POST | `/tasks` | Cria tarefa (`{"title": "..."}`) |

Documentação interativa automática: `http://localhost:8080/docs`

## Como rodar

Sem banco (modo memória, para testar rápido):

```bash
python -m app.main
```

Com banco Postgres:

```bash
DATABASE_URL=postgresql://app:app@localhost:5432/app python -m app.main
```

Testes:

```bash
pytest
```

## A prática de hoje

Sigam **na ordem**: `STEP-1.md` → `STEP-2.md` → `STEP-3.md`.

Cada arquivo tem ~10 minutos de trabalho. No final dos três, vocês terão **70% da Sprint 2 entregue**.

## Como abrir no Codespaces

1. **Fork** deste repositório para a conta do time.
2. No fork, clique em **Code** → aba **Codespaces** → **Create codespace on main**.
3. Aguardar 1-2 min na primeira vez. Pronto: VS Code no navegador, com Python e Docker já instalados, dependências baixadas.

> **Importante**: ao terminar a aula, parem o Codespace para não consumir cota: aba Codespaces → `...` → **Stop codespace**.
