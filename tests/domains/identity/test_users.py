import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    me = await client.get("/api/v1/users/me", headers=auth_headers)
    user_id = me.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
