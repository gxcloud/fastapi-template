# fastapi-template

Async-first, container-first, domain-driven FastAPI template for building large-scale Python web applications.

## Features

| Feature | Implementation |
|---------|---------------|
| **Async-first** | SQLAlchemy 2.0 async engine, asyncpg driver, async endpoints, async tests |
| **Domain-driven** | Code organized by business domain, not technical layer |
| **Container-first** | Multi-stage Docker build, Compose for dev/prod parity |
| **Repository pattern** | `BaseRepository[M]` with generic CRUD, deterministic ordering |
| **Service layer** | Business logic with ownership enforcement (403), duplicate checks (409) |
| **DI container** | dishka auto-wires dependencies by scope — no manual wiring |
| **JWT auth** | Access tokens via python-jose, password hashing via bcrypt with per-user salt |
| **OIDC ready** | OpenID Connect support for password-less authentication |
| **Password salting** | Explicit per-user salt (`secrets.token_hex(16)`) prepended before bcrypt |
| **CORS** | Configurable origins via pydantic-settings |
| **Migrations** | Async Alembic with auto-generation |
| **Code quality** | ruff (lint+format), mypy (strict mode), pre-commit hooks |
| **Testing** | pytest with testcontainers for disposable PostgreSQL |
| **CI/CD** | GitHub Actions workflow with lint + test jobs |
| **Error handling** | Structured JSON errors for all exception types |
| **Pagination** | Reusable `PaginationParams` + `PaginatedResponse[T]` |
| **Request logging** | Middleware logs method/path/status/duration + X-Request-ID |
| **Startup validation** | DB connectivity check on app launch |
| **Password strength** | Requires uppercase, lowercase, digit |

## Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python ≥ 3.12 | Language runtime |
| **Web framework** | FastAPI ≥ 0.115 | Async REST framework |
| **ORM** | SQLAlchemy 2.0 (asyncio) | Async ORM with `Mapped`/`mapped_column` style |
| **Database** | PostgreSQL + asyncpg | Async driver for Postgres |
| **Validation** | Pydantic v2 + pydantic-settings | Request/response schemas, env-based config |
| **DI** | dishka ≥ 1.4 | Scope-based dependency injection |
| **Auth** | python-jose + bcrypt | JWT tokens, password hashing |
| **Migrations** | Alembic (async) | Database schema versioning |
| **Package manager** | uv | Fast Python package manager |
| **Linting** | ruff | Linting + formatting |
| **Type checking** | mypy (strict mode) | Static type analysis |
| **Testing** | pytest + testcontainers | Async testing with disposable Postgres |
| **Container** | Docker + Compose | Multi-stage build, dev/prod parity |
| **CI** | GitHub Actions | Automated quality checks |

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

docker compose up --build
# App available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Local development

```bash
cp .env.example .env

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (including dev)
uv sync --extra dev

# Install project in editable mode
uv pip install -e .

# Run migrations
uv run alembic upgrade head

# Start dev server with hot-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify it works

```bash
curl http://localhost:8000/api/v1/health
# {"status": "ok"}
```

## Project Structure

```
fastapi-template/
├── src/
│   └── app/
│       ├── common/                     # Shared infrastructure
│       │   ├── base/
│       │   │   ├── model.py            # DeclarativeBase, UUIDMixin, TimestampMixin
│       │   │   └── repository.py       # Generic BaseRepository[M] (generic over model)
│       │   ├── config.py               # Pydantic Settings from env vars
│       │   ├── database.py              # Async engine + session factory (lazy)
│       │   ├── di.py                   # dishka AppProvider (scope-based DI)
│       │   ├── health.py               # Health check endpoint (no auth)
│       │   └── security.py             # JWT create/decode, bcrypt hash/verify with salt
│       ├── domains/
│       │   ├── identity/               # Bounded context: identity
│       │   │   ├── model.py            # User (id, email, hashed_password, password_salt, oidc_sub, oidc_provider, is_active, is_superuser)
│       │   │   ├── schemas.py          # UserCreate, UserUpdate, UserOIDCLogin, UserResponse
│       │   │   ├── repository.py       # UserRepository (find_by_email, list_by_ids, get_by_oidc)
│       │   │   ├── service.py          # UserService (register, authenticate, profile CRUD, OIDC login)
│       │   │   └── router.py           # auth_router (/auth) + user_router (/users)
│       │   └── items/                  # Bounded context: items
│       │       ├── model.py            # Item (id, title, description, is_public, owner_id FK)
│       │       ├── schemas.py          # ItemCreate, ItemUpdate, ItemResponse
│       │       ├── repository.py       # ItemRepository (list_by_owner, list_public)
│       │       ├── service.py          # ItemService (CRUD with ownership enforcement)
│       │       └── router.py           # router (/items)
│       ├── app.py                      # create_app() factory (CORS middleware, dishka setup)
│       └── main.py                     # uvicorn entrypoint (conditional reload)
├── tests/
│   ├── conftest.py                     # Shared fixtures (testcontainers, client, auth)
│   ├── common/
│   │   ├── test_health.py              # Health check test
│   │   └── test_security.py            # Security unit tests (salt, hash, JWT)
│   └── domains/
│       ├── identity/
│       │   ├── test_auth.py            # API: register, login, OIDC
│       │   ├── test_users.py           # API: get/me, list, get by id, update
│       │   ├── test_repository.py      # Unit: user data access
│       │   └── test_service.py         # Unit: user business logic
│       └── items/
│           ├── test_items.py           # API: item CRUD, ownership
│           ├── test_repository.py      # Unit: item data access
│           └── test_service.py         # Unit: item business logic
├── alembic/
│   ├── versions/
│   │   ├── 0001_create_users_and_items.py
│   │   └── 0002_add_oidc_and_salt.py
│   ├── env.py                          # Async migration runner
│   └── script.py.mako                  # Migration template
├── docker/
│   ├── Dockerfile                      # Multi-stage production build
│   └── Dockerfile.dev                  # Dev image with hot-reload
├── .github/workflows/
│   └── quality.yml                     # CI: lint + test (79 tests)
├── .opencode/skills/
│   ├── fastapi-test/SKILL.md           # OpenCode skill: testing patterns
│   └── fastapi-domain/SKILL.md         # OpenCode skill: creating new domains
├── .dockerignore
├── .env.example
├── .pre-commit-config.yaml
├── AGENTS.md                           # OpenCode project context
├── alembic.ini
├── docker-compose.yml                  # App + Postgres
├── docker-compose.override.yml         # Dev overrides (volumes, ports)
├── Makefile
├── pyproject.toml                      # Dependencies and tool config
├── README.md
└── uv.lock                             # Reproducible dependency lockfile
```

## Architecture

### Domain-Driven Design

Each business domain is a self-contained module under `src/app/domains/<name>/`. Every domain bundles exactly six files:

| File | Responsibility |
|------|---------------|
| `model.py` | SQLAlchemy 2.0 ORM model (extends `Base`, `UUIDMixin`, `TimestampMixin`) |
| `schemas.py` | Pydantic v2 request/response models (`model_config = {"from_attributes": True}`) |
| `repository.py` | Data access layer (extends `BaseRepository[Model]`) |
| `service.py` | Business logic with HTTPException for error cases |
| `router.py` | FastAPI endpoints (uses `DishkaRoute` for DI) |
| `__init__.py` | Empty |

### Request Lifecycle

```
Client → FastAPI → DishkaRoute → FromDishka[T] resolves dependencies → Router
    → Service (business logic) → Repository (data access) → AsyncSession → PostgreSQL
```

1. **DishkaRoute** wraps the endpoint with `inject()` to process `FromDishka[T]` annotations
2. **FromDishka[T]** requests dependency from dishka container by type hint
3. **AppProvider** (in `common/di.py`) provides instances at `APP` (singletons) or `REQUEST` scope
4. **Service** receives repository via constructor injection (auto-wired by dishka)
5. **Repository** receives `AsyncSession` from the request-scoped session provider
6. Session is committed on success, rolled back on exception

### Dependency Injection

dishka scopes control the lifecycle of each dependency:

| Scope | Lifecycle | Examples |
|-------|-----------|---------|
| `APP` | Created once, shared across all requests | `Settings` |
| `REQUEST` | Created per request, destroyed after response | `AsyncSession`, `UserRepository`, `UserService` |

Endpoints inject dependencies via `FromDishka[T]` — no manual `Depends(get_xxx_service)` helper functions needed:

```python
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: FromDishka[User]) -> User:
    return current_user
```

The `AppProvider` in `common/di.py` handles all wiring:

```python
@provide(scope=Scope.REQUEST)
def get_user_service(self, repo: UserRepository) -> UserService:
    return UserService(repo=repo)
```

### Repository Pattern

`BaseRepository[M: Base]` provides standard CRUD with determined ordering:

- `save(model)` — Persist new or existing entity (add/flush/refresh)
- `create(model)` — Alias for `save()` for readability with new entities
- `get(id)` — Fetch by UUID primary key
- `list(skip, limit)` — Paginated list ordered by `created_at desc`
- `delete(model)` — Remove and flush

### Service Layer

Services raise `HTTPException` for all error cases — never let SQLAlchemy exceptions bubble up:

| Scenario | Status | Detail |
|----------|--------|--------|
| Duplicate email | `409 Conflict` | "Email already registered" |
| Not found | `404 Not Found` | "{Entity} not found" |
| Wrong owner | `403 Forbidden` | "Not authorized to {action} this item" |
| Invalid credentials | `401 Unauthorized` | "Invalid credentials" |
| Invalid/expired token | `401 Unauthorized` | "Invalid or expired token" |
| Account deactivated | `403 Forbidden` | "Account deactivated" |

### Authentication & Authorization

- **Password hashing**: Each user gets a unique salt via `secrets.token_hex(16)`. The salt is prepended to the password before bcrypt hashing. OIDC users have no password or salt.
- **JWT tokens**: Access tokens signed with HS256. Configurable expiry via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **OIDC**: Users can authenticate via OpenID Connect. The `/auth/oidc` endpoint accepts provider, sub, and email. If the user exists, return them; if not, create a new user (just-in-time provisioning).
- **Active user check**: `get_current_user` dependency rejects deactivated accounts with `403`.
- **Item ownership**: Update and delete operations verify the authenticated user owns the item (`403` if not).

## API Reference

All endpoints are prefixed with `/api/v1`.

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Returns `{"status": "ok"}` |
| `GET` | `/health/ready` | No | DB connectivity check → `{"status":"ok","database":"connected"}` |

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | No | Register with email + password |
| `POST` | `/auth/login` | No | Login → returns JWT access token |
| `POST` | `/auth/oidc` | No | OIDC login (provider + sub) → returns user |

#### Register

```json
// POST /api/v1/auth/register
// Request
{"email": "user@example.com", "password": "securepassword123"}
// Response 201
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "oidc_sub": null,
  "oidc_provider": null
}
```

#### Login

```json
// POST /api/v1/auth/login
// Request
{"email": "user@example.com", "password": "securepassword123"}
// Response 200
{"access_token": "eyJ...", "token_type": "bearer"}
```

#### OIDC Login

```json
// POST /api/v1/auth/oidc
// Request
{"provider": "google", "sub": "google-user-id-123", "email": "user@gmail.com"}
// Response 200
{
  "id": "uuid",
  "email": "user@gmail.com",
  "is_active": true,
  "is_superuser": false,
  "oidc_sub": "google-user-id-123",
  "oidc_provider": "google"
}
```

### Users

All user endpoints require a valid JWT in the `Authorization: Bearer <token>` header.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/users/me` | Yes | Get current user profile |
| `GET` | `/users` | Yes | List all users |
| `GET` | `/users/{id}` | Yes | Get user by ID |
| `PATCH` | `/users/{id}` | Yes | Update user |

### Items

Item endpoints require a valid JWT for write operations.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/items` | Yes | Create item |
| `GET` | `/items` | No | List public items |
| `GET` | `/items/mine` | Yes | List current user's items |
| `GET` | `/items/{id}` | Yes | Get item by ID |
| `PATCH` | `/items/{id}` | Yes | Update item (owner only) |
| `DELETE` | `/items/{id}` | Yes | Delete item (owner only) |

## Commands

### Package management

```bash
uv sync                           # Install all dependencies
uv sync --extra dev               # Install including dev dependencies
uv pip install -e .               # Install project in editable mode
uv add <package>                  # Add a runtime dependency
uv add --dev <package>            # Add a dev dependency
uv lock                           # Update lockfile
```

### Development

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
make dev                          # Same as above via Makefile
```

### Testing

```bash
uv run pytest tests/ -v                              # Run all 79 tests
uv run pytest tests/ -v --cov=src/ --cov-report=term-missing  # With coverage
uv run pytest tests/domains/identity/test_auth.py -v  # Single file
uv run pytest tests/ -k "test_register"               # By name pattern
make test                                             # Via Makefile
```

### Code quality

```bash
uv run ruff check src/ tests/     # Lint
uv run ruff format --check src/ tests/  # Format check (CI-friendly)
uv run ruff format src/ tests/    # Auto-format
uv run mypy src/                  # Type check (strict mode)
make lint                         # Lint via Makefile
make format                       # Format via Makefile
make typecheck                    # Type check via Makefile
```

### Database

```bash
uv run alembic upgrade head       # Apply all pending migrations
uv run alembic downgrade -1       # Roll back one migration
uv run alembic revision --autogenerate -m "description"  # Create migration
make migrate-up                   # Migrate via Makefile
make migrate-create name=desc     # Create migration via Makefile
```

### Docker

```bash
docker compose up --build         # Start all services
docker compose up -d              # Start in background
docker compose logs -f            # Follow logs
docker compose down -v            # Stop and remove volumes
make docker-up                    # Via Makefile
make docker-down                  # Via Makefile
```

### Container management

```bash
docker compose up --build         # Build and start (production config)
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build  # Dev with overrides
```

### Misc

```bash
make clean                        # Remove virtual env and cache dirs
pre-commit run --all-files        # Run pre-commit hooks manually
```

## Testing

### Test structure

Tests mirror the domain-driven source layout. Each domain has three test files:

```
tests/
├── conftest.py                    # Shared fixtures
├── common/
│   ├── test_health.py             # Operational tests
│   └── test_security.py           # Unit: security functions (8 tests)
├── domains/
│   ├── identity/
│   │   ├── test_auth.py           # API: registration, login, OIDC (11 tests)
│   │   ├── test_users.py          # API: profile, list, update (9 tests)
│   │   ├── test_repository.py     # Unit: user data access (8 tests)
│   │   └── test_service.py        # Unit: user business logic (16 tests)
│   └── items/
│       ├── test_items.py          # API: CRUD, ownership (15 tests)
│       ├── test_repository.py     # Unit: item data access (8 tests)
│       └── test_service.py        # Unit: item business logic (8 tests)
```

**Total: 92 tests**

### Running tests

Tests require Docker (testcontainers auto-starts Postgres). In CI, a Postgres service container is used instead — set `DB_URL` and `SECRET_KEY` env vars to skip testcontainers.

### Writing tests

- **No `@pytest.mark.asyncio`** — `asyncio_mode = "auto"` in `pyproject.toml` handles it
- **Module-level imports from app are safe** — `create_app(db_url=...)` overrides the DB connection
- **Engine is autouse** — tables are created/dropped automatically for each test
- **Commit test data** — fixtures that create data for API tests must call `await session.commit()` so the app's session can see it
- **Salt-aware helpers** — use the `_hashed(pw)` pattern when creating test users directly

```python
# API test
async def test_my_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items")
    assert response.status_code == 200

# Auth-required test
async def test_protected(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200

# Repository test (needs salt)
async def test_repo_query(user_repo: UserRepository) -> None:
    from app.common.security import generate_salt, hash_password
    salt = generate_salt()
    user = User(email="t@example.com", hashed_password=hash_password("pass", salt), password_salt=salt)
    created = await user_repo.create(user)
    assert created.id is not None
```

### Test fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `postgres` | function | Starts testcontainers Postgres (skipped if `DB_URL` env var set) |
| `db_url` | function | Asyncpg connection URL |
| `engine` | function (autouse) | Creates/drops all tables |
| `session` | function | Per-test async session (auto-rollback) |
| `client` | function | httpx AsyncClient against fresh FastAPI app |
| `user_repo` | function | `UserRepository` with clean session |
| `item_repo` | function | `ItemRepository` with clean session |
| `user_service` | function | `UserService` wired with `user_repo` |
| `item_service` | function | `ItemService` wired with `item_repo` |
| `registered_user` | function | `(User, str)` — created user + JWT token (committed) |
| `auth_token` | function | JWT token string |
| `auth_headers` | function | `{"Authorization": "Bearer <token>"}` |

## Configuration

All configuration is driven by environment variables through `pydantic-settings`. Copy `.env.example` to `.env` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `false` | Enable debug mode |
| `DB_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/app` | Database URL |
| `DB_ECHO` | `false` | Log SQL statements |
| `DB_POOL_SIZE` | `20` | Connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Connection pool overflow |
| `SECRET_KEY` | `change-me` | JWT signing key **(change in production!)** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiry |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

## Adding a New Domain

1. Create the domain module:

```
src/app/domains/<name>/
├── __init__.py
├── model.py
├── schemas.py
├── repository.py
├── service.py
└── router.py
```

2. Register the repository and service in `src/app/common/di.py` (`AppProvider` class):

```python
@provide(scope=Scope.REQUEST)
def get_<name>_repo(self, session: AsyncSession) -> <Name>Repository:
    return <Name>Repository(session=session)

@provide(scope=Scope.REQUEST)
def get_<name>_service(self, repo: <Name>Repository) -> <Name>Service:
    return <Name>Service(repo=repo)
```

3. Mount the router in `src/app/app.py`:

```python
from app.domains.<name>.router import router as <name>_router
v1_router.include_router(<name>_router)
```

4. Generate and apply a migration:

```bash
uv run alembic revision --autogenerate -m "create <name> table"
uv run alembic upgrade head
```

5. Create test files in `tests/domains/<name>/`:
   - `test_<name>.py` — API tests
   - `test_repository.py` — data access tests
   - `test_service.py` — business logic tests

## Deployment

### Docker (production)

```bash
# Build and start
docker compose -f docker-compose.yml up --build -d

# Set required env vars
export SECRET_KEY="your-strong-production-secret"

# Monitor
docker compose logs -f
```

### Multi-stage build

The production `Dockerfile` uses a two-stage build:
1. **Builder stage**: Installs dependencies with `uv sync --frozen --no-dev`
2. **Runtime stage**: Slim Python image with only `.venv` and application code (~120 MB)

Health check is configured at `/api/v1/health` with 30s intervals.

## CI/CD

GitHub Actions runs on every push/PR to `main`:

### `quality` workflow

```yaml
lint:     ruff check + ruff format --check + mypy (strict)
test:     pytest with coverage (Postgres service container, 92 tests)
```

Test job uses a Postgres service container instead of testcontainers. The `postgres` fixture in `conftest.py` detects CI via the `CI` env var and falls back to the service container's `DB_URL`.

## Code Quality

- **ruff**: linting (`ruff check`) + formatting (`ruff format`). Configured in `pyproject.toml`.
- **mypy**: strict mode. Excludes `alembic/`. Configured in `pyproject.toml`.
- **pre-commit**: runs ruff (fix + format) and mypy before each commit.

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Project Conventions

- **Imports**: standard library → third-party → app modules (ruff auto-sorts)
- **Type hints**: always annotate return types and parameters. No `Any` unless unavoidable
- **Async**: all database operations use `async`/`await`. Synchronous helpers (hash, JWT) are pure functions
- **Return types**: always annotate endpoint return types (e.g., `-> User`, `-> list[Item]`)
- **Error handling**: services raise `HTTPException` with appropriate status codes. No SQLAlchemy exceptions in the API layer
- **Models**: SQLAlchemy 2.0 style (`Mapped`, `mapped_column`). UUID PKs + timestamp columns via mixins
- **Schemas**: Pydantic v2 with `model_config = {"from_attributes": True}` for ORM mode. Passwords validated with `Field(min_length=8)` and must contain uppercase, lowercase, and digit characters.
