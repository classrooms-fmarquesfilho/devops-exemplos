# STEP 1 — Pipeline de CI no GitHub Actions

**Objetivo**: a cada push, o GitHub deve rodar lint + testes automaticamente.

**Tempo estimado**: 10 minutos.

---

## 1.1. Verificar que o projeto roda localmente

No terminal do Codespaces:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Devem ver `4 passed`. Também rodem o lint:

```bash
ruff check app/ tests/
```

Devem ver `All checks passed!`. Se algo falhar aqui, o CI também vai falhar — então resolver primeiro.

## 1.2. Criar o workflow

Criar o arquivo `.github/workflows/ci.yml` com este conteúdo:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: ruff check app/ tests/

      - name: Test
        run: pytest -v
```

**Lendo o YAML:**
- `on:` define quando o workflow roda (a cada push em main e a cada PR)
- `jobs.test` é um job só, rodando numa VM Ubuntu nova
- `cache: 'pip'` deixa o build mais rápido nas próximas execuções
- Cada `name:` é uma etapa que aparece individualmente na interface do GitHub

## 1.3. Commitar e empurrar

```bash
git add .github/workflows/ci.yml
git commit -m "ci: pipeline inicial com lint e testes"
git push
```

## 1.4. Ver o pipeline rodando

No GitHub, aba **Actions**. Vocês devem ver o workflow rodando. Em ~30s:

- ✅ Verde: tudo certo.
- ❌ Vermelho: clicar no job para ver o que falhou.

## 1.5. **Quebrar de propósito** (importante!)

O pipeline só prova valor quando **pega um problema**. Vamos plantar dois erros, em momentos diferentes:

### 1.5.a — Quebrar o lint

Em `app/main.py`, adicionar no topo um import não usado:

```python
import json   # NÃO usado em lugar nenhum
```

Commit e push. Em ~30s o CI fica **vermelho** com mensagem clara:

```
F401 [*] `json` imported but unused
```

O CI travou a mudança **antes** dela chegar em main. Esse é o **1º Caminho** funcionando: nunca passar defeito adiante.

Reverter (apagar a linha), commitar, push de novo. Verde.

### 1.5.b — Quebrar um teste

Em `app/main.py`, mudar o status code de criação:

```python
@app.post("/tasks", response_model=TaskOut, status_code=200)  # era 201
```

Commit, push, e veja o teste `test_create_and_list_tasks` falhar:

```
assert response.status_code == 201
AssertionError: assert 200 == 201
```

Reverter e push. Verde.

---

## ✅ Checklist do STEP 1

- [ ] `.github/workflows/ci.yml` criado e commitado
- [ ] Pipeline rodou verde pelo menos uma vez
- [ ] Você viu o pipeline ficar vermelho ao plantar erro de **lint**
- [ ] Você viu o pipeline ficar vermelho ao plantar erro de **teste**
- [ ] Você corrigiu e ficou verde de novo

**Próximo**: `STEP-2.md` — Dockerfile multi-stage.
