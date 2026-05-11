from uuid import UUID

from app.common.security import hash_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.items.model import Item
from app.domains.items.repository import ItemRepository


async def test_create_item(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    user = User(email="owner@example.com", hashed_password=hash_password("pass"))
    owner = await user_repo.create(user)
    item = Item(title="Test Item", owner_id=owner.id)
    created = await item_repo.create(item)
    assert created.id is not None
    assert created.title == "Test Item"
    assert created.owner_id == owner.id


async def test_get_item(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    owner = await user_repo.create(
        User(email="get@example.com", hashed_password=hash_password("pass")),
    )
    item = await item_repo.create(Item(title="Get Test", owner_id=owner.id))
    found = await item_repo.get(item.id)
    assert found is not None
    assert found.title == "Get Test"


async def test_get_item_not_found(item_repo: ItemRepository) -> None:
    found = await item_repo.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert found is None


async def test_list_by_owner(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    owner = await user_repo.create(
        User(email="list@example.com", hashed_password=hash_password("pass")),
    )
    for i in range(3):
        await item_repo.create(
            Item(title=f"Item {i}", owner_id=owner.id),
        )
    items = await item_repo.list_by_owner(owner.id)
    assert len(items) == 3
    assert all(i.owner_id == owner.id for i in items)


async def test_list_public(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    owner = await user_repo.create(
        User(email="public@example.com", hashed_password=hash_password("pass")),
    )
    await item_repo.create(Item(title="Public", owner_id=owner.id, is_public=True))
    items = await item_repo.list_public()
    assert len(items) >= 1
    assert all(i.is_public for i in items)
