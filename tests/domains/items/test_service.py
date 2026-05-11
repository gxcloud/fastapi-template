from uuid import UUID

import pytest
from fastapi import HTTPException

from app.common.security import generate_salt, hash_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.items.schemas import ItemCreate, ItemUpdate
from app.domains.items.service import ItemService


def _hashed(pw: str) -> tuple[str, str]:
    salt = generate_salt()
    return hash_password(pw, salt), salt


async def test_create_item(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="owner@example.com", hashed_password=h, password_salt=s),
    )
    item = await item_service.create(
        ItemCreate(title="Test Item"),
        owner_id=owner.id,
    )
    assert item.title == "Test Item"
    assert item.owner_id == owner.id


async def test_get_item(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="get@example.com", hashed_password=h, password_salt=s),
    )
    created = await item_service.create(
        ItemCreate(title="Get Test"),
        owner_id=owner.id,
    )
    found = await item_service.get(created.id)
    assert found.title == "Get Test"


async def test_get_item_not_found(item_service: ItemService) -> None:
    with pytest.raises(HTTPException) as exc:
        await item_service.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert exc.value.status_code == 404


async def test_update_item(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="upd@example.com", hashed_password=h, password_salt=s),
    )
    created = await item_service.create(
        ItemCreate(title="Original"),
        owner_id=owner.id,
    )
    updated = await item_service.update(
        created.id,
        ItemUpdate(title="Updated"),
        owner_id=owner.id,
    )
    assert updated.title == "Updated"


async def test_update_item_wrong_owner(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="right@example.com", hashed_password=h, password_salt=s),
    )
    intruder = await user_repo.create(
        User(email="wrong@example.com", hashed_password=h, password_salt=s),
    )
    created = await item_service.create(
        ItemCreate(title="Mine"),
        owner_id=owner.id,
    )
    with pytest.raises(HTTPException) as exc:
        await item_service.update(
            created.id,
            ItemUpdate(title="Hacked"),
            owner_id=intruder.id,
        )
    assert exc.value.status_code == 403


async def test_delete_item(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="del@example.com", hashed_password=h, password_salt=s),
    )
    created = await item_service.create(
        ItemCreate(title="To Delete"),
        owner_id=owner.id,
    )
    await item_service.delete(created.id, owner_id=owner.id)
    with pytest.raises(HTTPException) as exc:
        await item_service.get(created.id)
    assert exc.value.status_code == 404


async def test_delete_item_wrong_owner(
    item_service: ItemService,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="right2@example.com", hashed_password=h, password_salt=s),
    )
    intruder = await user_repo.create(
        User(email="wrong2@example.com", hashed_password=h, password_salt=s),
    )
    created = await item_service.create(
        ItemCreate(title="Mine"),
        owner_id=owner.id,
    )
    with pytest.raises(HTTPException) as exc:
        await item_service.delete(created.id, owner_id=intruder.id)
    assert exc.value.status_code == 403
