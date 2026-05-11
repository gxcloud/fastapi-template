from httpx import AsyncClient


async def test_get_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


async def test_get_me_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_list_users(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


async def test_get_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    me = await client.get("/api/v1/users/me", headers=auth_headers)
    user_id = me.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


async def test_get_user_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_list_users_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users")
    assert response.status_code == 401


async def test_update_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    me = await client.get("/api/v1/users/me", headers=auth_headers)
    user_id = me.json()["id"]

    response = await client.patch(
        f"/api/v1/users/{user_id}",
        json={"email": "updated@example.com"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


async def test_update_user_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.patch(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        json={"email": "nope@example.com"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_user_unauthorized(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        json={"email": "nope@example.com"},
    )
    assert response.status_code == 401
