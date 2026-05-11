# fastapi-template

Async-first, container-first FastAPI template for large-scale projects.

## Stack

- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM with repository pattern
- **PostgreSQL** — database via asyncpg
- **Pydantic v2** — settings, request/response schemas
- **dishka** — dependency injection container (no manual wiring)
- **Alembic** — async database migrations
- **uv** — Python package manager
- **ruff** / **mypy** — linting, formatting, type checking
- **Docker** — multi-stage builds, Compose for dev/prod
- **testcontainers** — disposable Postgres for tests

## Quick Start

```bash
# Copy environment config
cp .env.example .env
# Edit .env with your SECRET_KEY

# Start with Docker
docker compose up --build

# Or locally with uv
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Project Structure

```
src/
  app/
    api/v1/endpoints/   # Route handlers
    core/               # Config, DB, security, DI provider
    models/             # SQLAlchemy ORM models
    schemas/            # Pydantic request/response models
    repositories/       # Data access layer
    services/           # Business logic layer
    app.py              # FastAPI app factory
    main.py             # Entrypoint
tests/
alembic/                # Database migrations
docker/                 # Dockerfiles
```

## Makefile

| Command | Description |
|---------|-------------|
| `make dev` | Run with hot-reload |
| `make lint` | Run ruff |
| `make format` | Format with ruff |
| `make typecheck` | Run mypy |
| `make test` | Run tests with coverage |
| `make docker-up` | Start Docker Compose |
| `make migrate-up` | Apply migrations |

## Architecture

- **App Factory** — `create_app()` enables test isolation
- **Repository Pattern** — data access abstracted behind interfaces
- **Service Layer** — business logic separated from HTTP
- **DI Container** — dishka auto-wires dependencies by scope
- **Container-First** — identical dev/prod environments via Docker
