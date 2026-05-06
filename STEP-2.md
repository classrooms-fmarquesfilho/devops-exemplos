# STEP 2 — Dockerfile multi-stage

**Objetivo**: empacotar a aplicação em uma imagem Docker pequena e reproduzível.

**Tempo estimado**: 10 minutos.

---

## 2.1. Criar o Dockerfile

Na raiz do repositório, criar o arquivo `Dockerfile`:

```dockerfile
# ---- Stage 1: builder ----
# Usamos a imagem completa para instalar dependências; pode precisar de
# compiladores para algumas libs (asyncpg compila C, por exemplo).
FROM python:3.12-slim AS builder

WORKDIR /build

# Cache de dependências: copiamos apenas o requirements primeiro.
# Se ele não mudar, o Docker reusa esta camada nos próximos builds.
COPY requirements.txt .

# --user instala em /root/.local; depois copiamos só essa pasta.
RUN pip install --user --no-cache-dir -r requirements.txt

# ---- Stage 2: runtime ----
FROM python:3.12-slim

# Boa prática: rodar como usuário não-root em produção
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Trazemos só os pacotes Python instalados, sem o pip cache, sem ferramentas de build.
COPY --from=builder --chown=app:app /root/.local /home/app/.local
COPY --chown=app:app app/ ./app/

# Garantir que os binários instalados via --user estão no PATH
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

CMD ["python", "-m", "app.main"]
```

**Por que multi-stage?** A imagem `python:3.12-slim` já é pequena, mas se vocês instalarem dependências que precisam compilar (como `asyncpg`), o `pip install` baixa compiladores temporários. Multi-stage permite usar uma stage "gorda" para instalar e copiar só o resultado para uma stage limpa.

**Por que rodar como `app` e não `root`?** Se um atacante explorar uma vulnerabilidade no servidor web, ele estará num usuário sem privilégios — não pode escrever no sistema, instalar pacotes, etc. Defesa em profundidade.

## 2.2. Criar um `.dockerignore`

Sem isso, o Docker copia o repo todo (incluindo `.git`, lixo de IDE, `__pycache__`) para o contexto de build. Mais lento e potencialmente vaza coisa.

Criar `.dockerignore`:

```
.git
.github
*.md
.vscode
.idea
.env
.env.*
__pycache__
*.pyc
.pytest_cache
.venv
venv
tests
```

## 2.3. Buildar localmente (no Codespaces)

```bash
docker build -t sprint2-api:dev .
```

A primeira vez leva ~1-2 min. Verificar o tamanho da imagem:

```bash
docker images sprint2-api:dev
```

Devem ver algo em torno de **150–200 MB**. Parece grande comparado ao Go (que daria 15 MB), mas é o **custo do interpretador Python** — e ainda é muito menos que uma imagem Python "completa" (~1 GB).

## 2.4. Rodar o container

```bash
docker run --rm -p 8080:8080 sprint2-api:dev
```

Em outro terminal:

```bash
curl localhost:8080/health
```

Devem ver `{"status":"ok","db":"ok"}` — o `db: ok` aqui é porque sem `DATABASE_URL` ele cai no store em memória. (No próximo passo conectamos um Postgres real.)

`Ctrl+C` para parar.

## 2.5. Adicionar build de imagem ao CI

Editar `.github/workflows/ci.yml` e adicionar **um novo job** depois do `test`:

```yaml
  docker:
    needs: test                       # só roda se os testes passarem
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false                 # só validar que builda
          tags: sprint2-api:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Commit e push:

```bash
git add Dockerfile .dockerignore .github/workflows/ci.yml
git commit -m "feat: dockerfile multi-stage + build no CI"
git push
```

Acompanhar a aba **Actions**. Agora o pipeline tem **dois jobs**: `test` e `docker`. O `docker` só roda se `test` passar — isso é o `needs:` no YAML.

---

## ✅ Checklist do STEP 2

- [ ] `Dockerfile` criado, multi-stage, rodando como não-root
- [ ] `.dockerignore` criado
- [ ] Imagem builda localmente em < 250 MB
- [ ] `docker run` responde em `/health`
- [ ] CI agora tem job `docker` que roda após `test`

**Próximo**: `STEP-3.md` — orquestrar app + Postgres com docker-compose.
