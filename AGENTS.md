# FastAPI Template — Domain-Driven, Async-First, Container-First

This is a Python project template for large-scale FastAPI applications.

## Stack

- **Python** 3.12+ (currently 3.13)
- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM with repository pattern
- **PostgreSQL** — database via asyncpg driver
- **Pydantic v2** — request/response schemas and settings
- **dishka** — dependency injection container (auto-wiring via `FromDishka[T]`)
- **Alembic** — async database migrations
- **uv** — Python package manager (not pip, not poetry)
- **JWT** — authentication via python-jose + bcrypt
- **CORS** — configurable via pydantic-settings
- **Docker** — multi-stage builds, Compose for dev/prod
- **testcontainers** — disposable PostgreSQL for tests

## Project Structure

```
src/app/
├── common/                     # Shared infrastructure
│   ├── base/
│   │   ├── model.py            # DeclarativeBase, UUIDMixin, TimestampMixin
│   │   └── repository.py       # Generic BaseRepository[M] (generic over model)
│   ├── config.py               # Pydantic Settings from env vars
│   ├── database.py              # Async engine + session factory (lazy)
│   ├── di.py                   # dishka AppProvider (scope-based DI)
│   ├── health.py               # Health check endpoint (no auth)
│   └── security.py             # JWT create/decode, bcrypt hash/verify
├── domains/
│   ├── identity/               # Bounded context: identity
│   │   ├── model.py            # User (id, email, hashed_password, password_salt, oidc_sub, oidc_provider, is_active, is_superuser)
│   │   ├── schemas.py          # UserCreate, UserUpdate, UserOIDCLogin, UserResponse
│   │   ├── repository.py       # UserRepository (find_by_email, list_by_ids)
│   │   ├── service.py          # UserService (register, authenticate, profile CRUD)
│   │   └── router.py           # auth_router (/auth) + user_router (/users)
│   └── items/                  # Bounded context: items
│       ├── model.py            # Item (id, title, description, is_public, owner_id FK)
│       ├── schemas.py          # ItemCreate, ItemUpdate, ItemResponse
│       ├── repository.py       # ItemRepository (list_by_owner, list_public)
│       ├── service.py          # ItemService (CRUD with ownership)
│       └── router.py           # router (/items)
├── app.py                      # create_app() factory (CORS middleware, dishka setup)
└── main.py                     # uvicorn entrypoint (conditional reload)
tests/
├── common/test_health.py
├── domains/
│   ├── identity/
│   │   ├── test_auth.py        # API: register, login
│   │   ├── test_users.py       # API: get/me, list, get by id
│   │   ├── test_repository.py  # Unit: user data access
│   │   └── test_service.py     # Unit: user business logic
│   └── items/
│       ├── test_items.py       # API: item CRUD
│       ├── test_repository.py  # Unit: item data access
│       └── test_service.py     # Unit: item business logic
└── conftest.py                 # testcontainers Postgres, test client, fixtures
```

## Key Architecture Decisions

1. **Domain-Driven Structure** — code is organized by business domain (identity, items), not by technical layer. Each domain bundles its model, schemas, repository, service, and router.

2. **Repository Pattern** — data access is abstracted behind `BaseRepository[M]`. Repositories receive an `AsyncSession` in their constructor. Use `save()` for both create and update (works for new and tracked entities). `list()` is ordered by `created_at desc` by default.

3. **Service Layer** — business logic lives in services, not endpoints. Services raise `HTTPException` for error cases (409 for duplicates, 404 for not found, 403 for unauthorized). Endpoints are thin — they call services and return results.

4. **dishka DI Container** — no manual dependency wiring. Define providers in `common/di.py` with scopes (`APP` for singletons, `REQUEST` for per-request). Endpoints use `FromDishka[T]` to inject dependencies. Routes must use `DishkaRoute` to enable `FromDishka` resolution.

5. **Security** — JWT tokens via python-jose. Password hashing via bcrypt with explicit per-user salt (NOT passlib). CORS middleware configured from settings. Active user check in `get_current_user` dependency. Item ownership enforced on update/delete. OIDC support for password-less authentication via `/auth/oidc` endpoint.

6. **Async Everything** — SQLAlchemy async engine/sessions, asyncpg driver, async endpoints, async Alembic migrations, async tests.

7. **Container-First** — `docker-compose.yml` defines app + postgres. Dev overrides in `docker-compose.override.yml` mount source code for hot-reload.

## Commands

```bash
# Always use uv, never pip
uv sync                           # Install all dependencies
uv sync --extra dev               # Install including dev deps

# Development
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing (requires Docker for testcontainers)
uv run pytest tests/ -v           # Run all tests (45 tests)
uv run pytest tests/ -v --cov=src/  # With coverage

# Code quality
uv run ruff check src/ tests/     # Lint
uv run ruff format --check src/ tests/  # Format check
uv run ruff format src/ tests/    # Auto-format
uv run mypy src/                  # Type check (strict mode)

# Database
uv run alembic upgrade head       # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration

# Docker
docker compose up --build         # Start everything
docker compose down -v            # Stop and clean volumes

# Make shortcuts
make dev              # hot-reload server
make test             # tests with coverage
make lint             # ruff check
make typecheck        # mypy
make migrate-up       # alembic upgrade head
make docker-up        # docker compose up --build
```

## Coding Conventions

- **Imports**: standard library → third-party → app modules. Use ruff for automatic sorting.
- **Type hints**: always annotate return types and parameters. No `Any` unless unavoidable.
- **Async**: all database operations use `async`/`await`. Synchronous helpers (hash_password, JWT) are fine as pure functions.
- **Return types on endpoints**: always annotate the return type of endpoint functions (e.g., `-> User`, `-> list[Item]`, `-> dict[str, str]`).
- **Error handling**: services raise `HTTPException` with appropriate status codes. Never let SQLAlchemy exceptions bubble up to the API layer.
- **Password salting**: Each user gets a unique `password_salt` via `secrets.token_hex(16)`. The salt is prepended to the password before bcrypt hashing. OIDC users have no password or salt.
- **OIDC**: Users can authenticate via OpenID Connect. The `/auth/oidc` endpoint accepts a provider, sub, and email. If the user exists, return them; otherwise create a new user (just-in-time provisioning).
- **Models**: use SQLAlchemy 2.0 style (`Mapped`, `mapped_column`). All tables have UUID primary keys and timestamp columns via mixins.
- **Schemas**: use Pydantic v2 style with `model_config = {"from_attributes": True}` for ORM mode. Validate passwords with `Field(min_length=8)`.
- **Password salting**: Each user gets a unique `password_salt` via `secrets.token_hex(16)`. The salt is prepended to the password before bcrypt hashing. OIDC users have no password or salt.
- **OIDC**: Users can authenticate via OpenID Connect. The `/auth/oidc` endpoint accepts a provider, sub, and email. If the user exists, return them; otherwise create a new user (just-in-time provisioning).

## Dependencies

### Runtime
- `fastapi>=0.115` — web framework
- `uvicorn[standard]` — ASGI server
- `sqlalchemy[asyncio]>=2.0` — async ORM
- `asyncpg` — PostgreSQL async driver
- `alembic` — migrations
- `pydantic>=2.10`, `pydantic-settings>=2.7` — validation and config
- `python-jose[cryptography]` — JWT tokens
- `bcrypt>=4.0` — password hashing (NOT passlib, which is incompatible with bcrypt 5.0)
- `dishka>=1.4` — DI container

### Dev
- `pytest`, `pytest-asyncio`, `pytest-cov` — testing
- `httpx` — async test client for FastAPI
- `testcontainers[postgres]` — disposable PostgreSQL in tests
- `factory-boy` — test data factories
- `ruff` — linting and formatting
- `mypy` — type checking (strict mode)
- `pre-commit` — git hooks

## Testing Notes

- All 52 tests require Docker (testcontainers starts a real PostgreSQL container).
- New domains need three test files: `test_api.py`, `test_repository.py`, `test_service.py`.
- `asyncio_mode = "auto"` in pytest config — do NOT add `@pytest.mark.asyncio` on test functions.
- The `engine` fixture is `autouse=True` — tables create/drop automatically for every test.
- The `client` fixture creates a fresh FastAPI app with a test-specific DB URL via `create_app(db_url=...)`.
- The `auth_headers` fixture provides a valid JWT for a pre-registered test user.
- Module-level imports from app modules in conftest.py are safe because `create_app()` overrides the DB URL.
- New domains need three test files: `test_api.py`, `test_repository.py`, `test_service.py`.

## Git Workflow

- Commits should be atomic and focused on a single concern.
- Commit messages should be descriptive: what changed and why.
- `uv.lock` should be committed for reproducibility.
