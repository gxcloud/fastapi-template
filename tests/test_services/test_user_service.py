import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user(user_service: UserService) -> None:
    user = await user_service.create(
        UserCreate(email="new@example.com", password="password123"),
    )
    assert user.email == "new@example.com"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_duplicate_email(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="dup@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.create(
            UserCreate(email="dup@example.com", password="password123"),
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_authenticate(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="auth@example.com", password="password123"),
    )
    user = await user_service.authenticate("auth@example.com", "password123")
    assert user.email == "auth@example.com"


@pytest.mark.asyncio
async def test_authenticate_wrong_password(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="wrong@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.authenticate("wrong@example.com", "wrongpass")
    assert exc.value.status_code == 401
