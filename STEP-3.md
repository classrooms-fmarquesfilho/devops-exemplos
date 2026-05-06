# STEP 3 — docker-compose: app + Postgres

**Objetivo**: um único comando sobe a API conectada a um banco de verdade.

**Tempo estimado**: 10 minutos.

---

## 3.1. Criar o `docker-compose.yml`

Na raiz do repositório:

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
      PORT: "8080"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

**Pontos importantes:**
- `depends_on` com `condition: service_healthy` garante que a API só sobe **depois** que o banco passou no healthcheck. Sem isso, a API tenta conectar antes do Postgres estar pronto e crasha.
- `pgdata` é um volume nomeado: os dados sobrevivem a `docker compose down`.
- A API resolve o host `db` automaticamente (rede interna do compose).

## 3.2. Subir tudo

```bash
docker compose up --build
```

Vão ver:

1. Imagem da API sendo construída
2. Postgres baixando e iniciando
3. Healthcheck do Postgres passando ✓
4. API subindo e logando `Uvicorn running on http://0.0.0.0:8080`

## 3.3. Testar a API conectada ao banco

Em outro terminal:

```bash
# health agora deve mostrar db: ok (mas dessa vez Postgres real)
curl localhost:8080/health

# criar tarefa
curl -X POST localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"primeira task no banco real"}'

# listar
curl localhost:8080/tasks
```

Devem ver a tarefa criada com `id`, `title` e `created_at`.

## 3.4. Provar que o banco persiste

```bash
docker compose down                   # derruba os containers
docker compose up                     # sobe de novo
curl localhost:8080/tasks             # tarefa ainda está lá
```

A tarefa sobrevive porque o volume `pgdata` é persistente. Se quiserem zerar mesmo:

```bash
docker compose down -v                # -v apaga os volumes
```

## 3.5. Parar

`Ctrl+C` no terminal onde está rodando, depois:

```bash
docker compose down
```

## 3.6. Commitar

```bash
git add docker-compose.yml
git commit -m "feat: compose com api + postgres healthchecked"
git push
```

---

## ✅ Checklist do STEP 3

- [ ] `docker-compose.yml` criado com api + db + healthcheck
- [ ] `docker compose up --build` sobe tudo sem erro
- [ ] `/health` retorna `db: ok` com Postgres real
- [ ] Conseguiram criar e listar tarefas via `curl`
- [ ] Dados persistem entre `down` e `up`

---

# 🎯 Onde vocês estão agora

Se completaram os 3 STEPs:

| Entregável Sprint 2 | Status |
|---|---|
| Pipeline CI/CD funcionando | ✅ Pronto |
| Dockerfile | ✅ Pronto |
| Docker-compose com app + dependência | ✅ Pronto |
| Métricas DORA | ⬜ Falta |
| Retrospectiva | ⬜ Falta |
| Vídeo 8 min | ⬜ Falta |

**3 de 6 entregáveis em 30 minutos.** O resto é trabalho da sprint, mas vocês têm a base técnica para focar nas reflexões.

## Para o vídeo, **gravem agora** mostrando:

1. Push que fica verde no Actions
2. Push com erro plantado que fica vermelho
3. `docker compose up` subindo tudo
4. `curl` na API funcionando (e o `/docs` automático do FastAPI)

Esses 4 clipes já cobrem os primeiros 5 minutos do vídeo.
