import pytest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_user(user_service) -> None:
    from app.domains.identity.schemas import UserCreate

    user = await user_service.create(
        UserCreate(email="new@example.com", password="password123"),
    )
    assert user.email == "new@example.com"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_duplicate_email(user_service) -> None:
    from app.domains.identity.schemas import UserCreate

    await user_service.create(
        UserCreate(email="dup@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.create(
            UserCreate(email="dup@example.com", password="password123"),
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_authenticate(user_service) -> None:
    from app.domains.identity.schemas import UserCreate

    await user_service.create(
        UserCreate(email="auth@example.com", password="password123"),
    )
    user = await user_service.authenticate("auth@example.com", "password123")
    assert user.email == "auth@example.com"


@pytest.mark.asyncio
async def test_authenticate_wrong_password(user_service) -> None:
    from app.domains.identity.schemas import UserCreate

    await user_service.create(
        UserCreate(email="wrong@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.authenticate("wrong@example.com", "wrongpass")
    assert exc.value.status_code == 401
