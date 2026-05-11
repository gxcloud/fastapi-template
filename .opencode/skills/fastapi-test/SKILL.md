---
name: fastapi-test
description: Write and run tests using testcontainers PostgreSQL in a FastAPI domain-driven project
---

## Test Structure

Tests mirror the domain-driven structure:
```
tests/
├── conftest.py                    # Shared fixtures (postgres, engine, client, etc.)
├── common/test_health.py          # Infrastructure tests (no DB needed)
└── domains/
    ├── identity/
    │   ├── test_auth.py           # API-level auth tests (via httpx AsyncClient)
    │   ├── test_users.py          # API-level user tests (via httpx AsyncClient)
    │   ├── test_repository.py     # Unit: data access (lazy imports!)
    │   └── test_service.py        # Unit: business logic (lazy imports!)
    └── items/
        └── test_items.py          # API-level item CRUD tests
```

## Critical: Lazy Imports in Tests

NEVER import `from app.app import create_app` or `from app.common.config import settings` at module level in any test file. Always import inside fixtures or test functions:

```python
# WRONG — will use default settings, not test DB:
from app.app import create_app

# RIGHT — imports happen after fixtures set env vars:
async def my_test(client):
    from app.app import create_app  # OK, inside function
```

This applies to any import that could transitively import `app.common.config`.

## Available Fixtures (from conftest.py)

- `postgres` — starts a testcontainers PostgreSQL container
- `db_url` — the asyncpg connection URL from the container
- `engine` — creates/drops all tables (SQLAlchemy metadata)
- `session` — per-test async session (auto-rollback after test)
- `client` — httpx AsyncClient against a fresh FastAPI app (tables created)
- `user_repo` — UserRepository with a clean session
- `item_repo` — ItemRepository with a clean session
- `user_service` — UserService wired with user_repo
- `item_service` — ItemService wired with item_repo
- `auth_token` — registers a test user and returns a JWT token
- `auth_headers` — `{"Authorization": "Bearer <token>"}` dict

## Running Tests

```bash
# All tests (requires Docker running)
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=src/ --cov-report=term-missing

# Specific file
uv run pytest tests/domains/identity/test_auth.py -v

# Quick test (no coverage)
uv run pytest tests/ -x --no-header -q
```

## Writing New Tests

### API-level test (uses client fixture)
```python
@pytest.mark.asyncio
async def test_my_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
```

### Auth-required API test
```python
@pytest.mark.asyncio
async def test_protected_endpoint(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
```

### Repository test (uses session directly)
```python
@pytest.mark.asyncio
async def test_repo_query(user_repo) -> None:
    from app.common.security import hash_password  # lazy!
    from app.domains.identity.model import User     # lazy!

    user = User(email="test@example.com", hashed_password=hash_password("pass"))
    created = await user_repo.create(user)
    assert created.id is not None
```

### Service test
```python
@pytest.mark.asyncio
async def test_business_logic(user_service) -> None:
    from app.domains.identity.schemas import UserCreate  # lazy!

    user = await user_service.create(
        UserCreate(email="test@example.com", password="password123"),
    )
    assert user.is_active is True
```
