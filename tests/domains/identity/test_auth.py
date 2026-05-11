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
    assert data["oidc_sub"] is None
    assert data["oidc_provider"] is None
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


async def test_register_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert response.status_code == 422


async def test_register_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "1234567"},
    )
    assert response.status_code == 422


async def test_register_no_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "nopass@example.com"},
    )
    assert response.status_code == 422


async def test_register_both_password_and_oidc(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "both@example.com",
            "password": "password123",
            "oidc_sub": "abc123",
            "oidc_provider": "google",
        },
    )
    assert response.status_code == 422


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


async def test_oidc_login_new_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/oidc",
        json={
            "provider": "google",
            "sub": "google-123",
            "email": "oidc-new@example.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "oidc-new@example.com"
    assert data["oidc_sub"] == "google-123"
    assert data["oidc_provider"] == "google"


async def test_login_with_oidc_user(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/oidc",
        json={"provider": "google", "sub": "oidc-only", "email": "oidconly@example.com"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "oidconly@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401


async def test_oidc_login_existing_user(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/oidc",
        json={
            "provider": "github",
            "sub": "gh-456",
            "email": "oidc-existing@example.com",
        },
    )
    response = await client.post(
        "/api/v1/auth/oidc",
        json={
            "provider": "github",
            "sub": "gh-456",
            "email": "other@example.com",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "oidc-existing@example.com"
