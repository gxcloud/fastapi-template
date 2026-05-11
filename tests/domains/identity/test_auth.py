from httpx import AsyncClient


async def test_register(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123"},
    )
    assert response.status_code == 409


async def test_login(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
