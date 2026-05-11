from sqlalchemy.ext.asyncio import AsyncSession

from app.common.security import generate_salt, hash_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository


def _hashed(pw: str) -> tuple[str, str]:
    salt = generate_salt()
    return hash_password(pw, salt), salt


async def test_create_user(user_repo: UserRepository) -> None:
    h, s = _hashed("pass")
    user = User(email="test@example.com", hashed_password=h, password_salt=s)
    created = await user_repo.create(user)
    assert created.id is not None
    assert created.email == "test@example.com"


async def test_get_by_email(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    h, s = _hashed("pass")
    user = User(email="find@example.com", hashed_password=h, password_salt=s)
    session.add(user)
    await session.flush()

    found = await user_repo.get_by_email("find@example.com")
    assert found is not None
    assert found.email == "find@example.com"


async def test_get_by_email_not_found(user_repo: UserRepository) -> None:
    found = await user_repo.get_by_email("missing@example.com")
    assert found is None


async def test_list_users(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    for i in range(3):
        h, s = _hashed("pass")
        session.add(
            User(email=f"user{i}@example.com", hashed_password=h, password_salt=s),
        )
    await session.flush()

    users = await user_repo.list()
    assert len(users) >= 3


async def test_get_by_oidc(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    user = User(email="oidc@example.com", oidc_sub="sub-1", oidc_provider="google")
    session.add(user)
    await session.flush()

    found = await user_repo.get_by_oidc("google", "sub-1")
    assert found is not None
    assert found.email == "oidc@example.com"


async def test_get_by_oidc_not_found(user_repo: UserRepository) -> None:
    found = await user_repo.get_by_oidc("google", "nonexistent")
    assert found is None


async def test_save_existing_user(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    h, s = _hashed("pass")
    user = User(email="save@example.com", hashed_password=h, password_salt=s)
    session.add(user)
    await session.flush()

    user.email = "updated@example.com"
    updated = await user_repo.save(user)
    assert updated.email == "updated@example.com"

    found = await user_repo.get_by_email("updated@example.com")
    assert found is not None


async def test_delete_user(
    user_repo: UserRepository,
    session: AsyncSession,
) -> None:
    h, s = _hashed("pass")
    user = User(email="delete@example.com", hashed_password=h, password_salt=s)
    session.add(user)
    await session.flush()

    await user_repo.delete(user)
    found = await user_repo.get(user.id)
    assert found is None
