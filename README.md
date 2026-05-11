# fastapi-template

Async-first, container-first FastAPI template for large-scale projects.

## Stack

- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM with repository pattern
- **PostgreSQL** — database via asyncpg
- **Pydantic v2** — settings, request/response schemas
- **dishka** — DI container (auto-wiring, no manual helpers)
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
    common/                     # Shared infrastructure
      base/
        model.py                # DeclarativeBase, UUIDMixin, TimestampMixin
        repository.py           # Generic BaseRepository[M]
      config.py                 # Pydantic settings from env
      database.py               # Async SQLAlchemy engine
      di.py                     # dishka DI provider (scope-based wiring)
      health.py                 # Health check endpoint
      security.py               # JWT tokens, bcrypt hashing
    domains/
      identity/                 # Identity bounded context
        model.py, schemas.py, repository.py, service.py, router.py
      items/                    # Items bounded context
        model.py, schemas.py, repository.py, service.py, router.py
    app.py                      # FastAPI app factory (CORS, dishka)
    main.py                     # uvicorn entrypoint
tests/
  common/                       # Infrastructure tests
  domains/                      # Per-domain tests (API, repository, service)
  conftest.py                   # Shared fixtures
alembic/                        # Database migrations
docker/                         # Dockerfiles
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

- **Domain-Driven** — code organized by business domain (identity, items) not technical layers
- **App Factory** — `create_app()` accepts optional `db_url` for test isolation
- **Repository Pattern** — `BaseRepository.save()` for create and update, ordered by `created_at`
- **Service Layer** — business logic with ownership enforcement (403), duplicate checks (409)
- **DI Container** — dishka auto-wires dependencies by scope via `FromDishka[T]` + `DishkaRoute`
- **Security** — JWT auth, bcrypt hashing, CORS middleware, active user check
- **Container-First** — identical dev/prod environments via Docker
