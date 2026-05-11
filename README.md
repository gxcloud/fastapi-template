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
    common/                     # Shared infrastructure
      base/
        model.py                # DeclarativeBase, UUIDMixin, TimestampMixin
        repository.py           # Generic BaseRepository[M]
      config.py                 # Pydantic settings from env
      database.py               # Async SQLAlchemy engine + session factory
      di.py                     # dishka DI provider (scope-based wiring)
      health.py                 # Health check endpoint
      security.py               # JWT tokens, bcrypt hashing
    domains/
      identity/                 # Identity bounded context
        model.py                # User ORM model
        schemas.py              # UserCreate, UserUpdate, UserResponse
        repository.py           # UserRepository (data access)
        service.py              # UserService (business logic)
        router.py               # /auth and /users endpoints
      items/                    # Items bounded context
        model.py                # Item ORM model
        schemas.py              # ItemCreate, ItemUpdate, ItemResponse
        repository.py           # ItemRepository (data access)
        service.py              # ItemService (business logic)
        router.py               # /items endpoints
    app.py                      # FastAPI app factory
    main.py                     # uvicorn entrypoint
tests/
  common/                       # Infrastructure tests
  domains/
    identity/                   # Identity domain tests
    items/                      # Items domain tests
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
- **App Factory** — `create_app()` enables test isolation
- **Repository Pattern** — data access abstracted behind domain-specific repositories
- **Service Layer** — business logic lives alongside its domain, separated from HTTP
- **DI Container** — dishka auto-wires dependencies by scope, no manual wiring
- **Container-First** — identical dev/prod environments via Docker
