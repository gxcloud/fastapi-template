---
name: fastapi-test
description: Write and run tests using testcontainers PostgreSQL in a FastAPI domain-driven project
---

## Test Structure

Tests mirror the domain-driven structure — each domain has three test files:
```
tests/
├── conftest.py                    # Shared fixtures (postgres, engine, client, etc.)
├── common/test_health.py          # Infrastructure tests (no DB needed)
└── domains/
    ├── identity/
    │   ├── test_auth.py           # API-level auth tests (via httpx AsyncClient)
    │   ├── test_users.py          # API-level user tests (via httpx AsyncClient)
    │   ├── test_repository.py     # Unit: data access
    │   └── test_service.py        # Unit: business logic
    └── items/
        ├── test_items.py          # API-level item CRUD tests
        ├── test_repository.py     # Unit: data access
        └── test_service.py        # Unit: business logic + ownership
```

## Key Rules

1. **No `@pytest.mark.asyncio`** — `asyncio_mode = "auto"` in pyproject.toml handles it.
2. **Module-level imports are safe** — `create_app()` accepts `db_url` override, so the global `settings` singleton doesn't matter.
3. **Always commit data fixtures** — if a fixture creates data for the API client, call `await session.commit()` so the app's session can see it.
4. **New domains need three test files** — API (httpx), repository (SQL), service (business logic).

## Available Fixtures (from conftest.py)

- `postgres` — starts a testcontainers PostgreSQL container
- `db_url` — the asyncpg connection URL from the container
- `engine` — `autouse=True` — creates/drops all tables for every test
- `session` — per-test async session (auto-rollback after test)
- `client` — httpx AsyncClient against a fresh FastAPI app
- `user_repo` — UserRepository with a clean session
- `item_repo` — ItemRepository with a clean session
- `user_service` — UserService wired with user_repo
- `item_service` — ItemService wired with item_repo
- `registered_user` — `tuple[User, str]` — created user + JWT token (committed)
- `auth_token` — JWT token string from `registered_user`
- `auth_headers` — `{"Authorization": "Bearer <token>"}` dict

## Running Tests

```bash
# All tests (requires Docker running)
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=src/ --cov-report=term-missing

# Specific test file
uv run pytest tests/domains/identity/test_auth.py -v
```

## Writing New Tests

### API-level test (uses client fixture)
```python
async def test_my_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
```

### Auth-required API test
```python
async def test_protected_endpoint(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
```

### Repository test
```python
async def test_repo_query(user_repo: UserRepository) -> None:
    from app.common.security import hash_password
    from app.domains.identity.model import User

    user = User(email="test@example.com", hashed_password=hash_password("pass"))
    created = await user_repo.create(user)
    assert created.id is not None
```

### Service test
```python
async def test_business_logic(user_service: UserService) -> None:
    user = await user_service.create(
        UserCreate(email="test@example.com", password="password123"),
    )
    assert user.is_active is True
```
