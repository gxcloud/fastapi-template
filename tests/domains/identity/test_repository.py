import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.security import hash_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(user_repo: UserRepository) -> None:
    user = User(email="test@example.com", hashed_password=hash_password("pass"))
    created = await user_repo.create(user)
    assert created.id is not None
    assert created.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_by_email(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    user = User(email="find@example.com", hashed_password=hash_password("pass"))
    session.add(user)
    await session.flush()

    found = await user_repo.get_by_email("find@example.com")
    assert found is not None
    assert found.email == "find@example.com"


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_repo: UserRepository) -> None:
    found = await user_repo.get_by_email("missing@example.com")
    assert found is None


@pytest.mark.asyncio
async def test_list_users(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    for i in range(3):
        session.add(
            User(email=f"user{i}@example.com", hashed_password=hash_password("pass")),
        )
    await session.flush()

    users = await user_repo.list()
    assert len(users) >= 3
