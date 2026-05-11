from httpx import AsyncClient


async def test_create_item(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "A test item"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["is_public"] is False
    assert "id" in data
    assert "owner_id" in data


async def test_create_item_unauthorized(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/items",
        json={"title": "Test Item"},
    )
    assert response.status_code == 401


async def test_list_public_items(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    await client.post(
        "/api/v1/items",
        json={"title": "Public Item", "is_public": True},
        headers=auth_headers,
    )
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(item["is_public"] for item in data)


async def test_list_my_items(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    await client.post(
        "/api/v1/items",
        json={"title": "My Item"},
        headers=auth_headers,
    )
    response = await client.get("/api/v1/items/mine", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "My Item"


async def test_list_my_items_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items/mine")
    assert response.status_code == 401


async def test_get_item(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    created = await client.post(
        "/api/v1/items",
        json={"title": "Get Test Item"},
        headers=auth_headers,
    )
    item_id = created.json()["id"]

    response = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test Item"


async def test_get_item_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/api/v1/items/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_item(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    created = await client.post(
        "/api/v1/items",
        json={"title": "Original"},
        headers=auth_headers,
    )
    item_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/items/{item_id}",
        json={"title": "Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


async def test_update_item_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.patch(
        "/api/v1/items/00000000-0000-0000-0000-000000000000",
        json={"title": "Nope"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_delete_item(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    created = await client.post(
        "/api/v1/items",
        json={"title": "To Delete"},
        headers=auth_headers,
    )
    item_id = created.json()["id"]

    response = await client.delete(
        f"/api/v1/items/{item_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


async def test_delete_item_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.delete(
        "/api/v1/items/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
