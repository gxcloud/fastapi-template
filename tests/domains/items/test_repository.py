from uuid import UUID

from app.common.security import generate_salt, hash_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.items.model import Item
from app.domains.items.repository import ItemRepository


def _hashed(pw: str) -> tuple[str, str]:
    salt = generate_salt()
    return hash_password(pw, salt), salt


async def test_create_item(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    user = User(email="owner@example.com", hashed_password=h, password_salt=s)
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
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="get@example.com", hashed_password=h, password_salt=s),
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
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="list@example.com", hashed_password=h, password_salt=s),
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
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="public@example.com", hashed_password=h, password_salt=s),
    )
    await item_repo.create(Item(title="Public", owner_id=owner.id, is_public=True))
    items = await item_repo.list_public()
    assert len(items) >= 1
    assert all(i.is_public for i in items)


async def test_save_existing_item(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="saveitem@example.com", hashed_password=h, password_salt=s),
    )
    item = await item_repo.create(Item(title="Original", owner_id=owner.id))
    item.title = "Updated"
    updated = await item_repo.save(item)
    assert updated.title == "Updated"


async def test_delete_item(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="delitem@example.com", hashed_password=h, password_salt=s),
    )
    item = await item_repo.create(Item(title="To Delete", owner_id=owner.id))
    await item_repo.delete(item)
    assert await item_repo.get(item.id) is None


async def test_list_ordering(
    item_repo: ItemRepository,
    user_repo: UserRepository,
) -> None:
    h, s = _hashed("pass")
    owner = await user_repo.create(
        User(email="order@example.com", hashed_password=h, password_salt=s),
    )
    first = await item_repo.create(Item(title="First", owner_id=owner.id))
    await item_repo.create(Item(title="Second", owner_id=owner.id))
    third = await item_repo.create(Item(title="Third", owner_id=owner.id))

    items = await item_repo.list()
    assert len(items) >= 3
    assert items[0].id == third.id
    assert items[-1].id == first.id
