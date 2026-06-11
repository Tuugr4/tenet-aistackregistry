# tenet-aistackregistry

Registry microservice for the AI bill of materials of your applications: which model,
which prompt version, which dataset, embedding index, vector DB, eval result, fine-tune
and provider an app actually uses. Everything is recorded over a REST API and exported
as plain JSON, CycloneDX 1.6 ML-BOM or a Markdown report.

## Stack

- Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic
- PostgreSQL (Docker Compose), SQLite in tests

## Quick start

```bash
docker compose up -d db
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"
.venv/Scripts/alembic upgrade head
.venv/Scripts/uvicorn app.main:app --reload
```

Or everything in containers:

```bash
docker compose up --build
```

Swagger UI: http://localhost:8000/docs

## API overview

CRUD under `/api/v1` for: `applications`, `providers`, `models`, `prompts`, `datasets`,
`fine-tunes`, `embedding-indexes`, `vector-dbs`, `eval-results`.

Link components to an application, then export its AIBOM:

```bash
# create an app
curl -X POST localhost:8000/api/v1/applications \
  -H 'Content-Type: application/json' \
  -d '{"name":"Support Bot","slug":"support-bot","environment":"prod"}'

# register a model
curl -X POST localhost:8000/api/v1/models \
  -H 'Content-Type: application/json' \
  -d '{"name":"GPT-4o mini","model_id":"gpt-4o-mini","context_window":128000}'

# link it
curl -X POST localhost:8000/api/v1/applications/<app_id>/links \
  -H 'Content-Type: application/json' \
  -d '{"component_type":"model","component_id":"<model_id>","role":"chat"}'

# exports
curl localhost:8000/api/v1/applications/<app_id>/aibom
curl localhost:8000/api/v1/applications/<app_id>/aibom?format=cyclonedx
curl localhost:8000/api/v1/applications/<app_id>/report.md
```

Prompts are versioned (`name` + `version` unique) and get a sha256 content hash
automatically. Eval results point at a model or a prompt via `target_type` / `target_id`.
Every record carries a free-form `metadata` object.

## Tests

```bash
.venv/Scripts/pytest
```

Tests run on in-memory SQLite, no Postgres needed.
