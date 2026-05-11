from uuid import UUID

import pytest
from fastapi import HTTPException

from app.domains.identity.schemas import UserCreate, UserUpdate
from app.domains.identity.service import UserService


async def test_create_user(user_service: UserService) -> None:
    user = await user_service.create(
        UserCreate(email="new@example.com", password="password123"),
    )
    assert user.email == "new@example.com"
    assert user.is_active is True


async def test_create_duplicate_email(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="dup@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.create(
            UserCreate(email="dup@example.com", password="password123"),
        )
    assert exc.value.status_code == 409


async def test_get_user(user_service: UserService) -> None:
    created = await user_service.create(
        UserCreate(email="get@example.com", password="password123"),
    )
    user = await user_service.get(created.id)
    assert user.id == created.id
    assert user.email == "get@example.com"


async def test_get_user_not_found(user_service: UserService) -> None:
    with pytest.raises(HTTPException) as exc:
        await user_service.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert exc.value.status_code == 404


async def test_update_user(user_service: UserService) -> None:
    created = await user_service.create(
        UserCreate(email="update@example.com", password="password123"),
    )
    updated = await user_service.update(
        created.id,
        UserUpdate(email="updated@example.com"),
    )
    assert updated.email == "updated@example.com"


async def test_update_user_duplicate_email(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="first@example.com", password="password123"),
    )
    second = await user_service.create(
        UserCreate(email="second@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.update(
            second.id,
            UserUpdate(email="first@example.com"),
        )
    assert exc.value.status_code == 409


async def test_authenticate(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="auth@example.com", password="password123"),
    )
    user = await user_service.authenticate("auth@example.com", "password123")
    assert user.email == "auth@example.com"


async def test_authenticate_wrong_password(user_service: UserService) -> None:
    await user_service.create(
        UserCreate(email="wrong@example.com", password="password123"),
    )
    with pytest.raises(HTTPException) as exc:
        await user_service.authenticate("wrong@example.com", "wrongpass")
    assert exc.value.status_code == 401


async def test_create_oidc_user(user_service: UserService) -> None:
    user = await user_service.create(
        UserCreate(
            email="oidc@example.com",
            oidc_sub="sub-oidc-1",
            oidc_provider="google",
        ),
    )
    assert user.email == "oidc@example.com"
    assert user.oidc_sub == "sub-oidc-1"
    assert user.oidc_provider == "google"
    assert user.hashed_password is None
    assert user.password_salt is None


async def test_authenticate_oidc_new_user(user_service: UserService) -> None:
    from app.domains.identity.schemas import UserOIDCLogin

    user = await user_service.authenticate_oidc(
        UserOIDCLogin(
            provider="github",
            sub="gh-789",
            email="oidc-auth@example.com",
        ),
    )
    assert user.email == "oidc-auth@example.com"
    assert user.oidc_provider == "github"
    assert user.oidc_sub == "gh-789"


async def test_authenticate_oidc_existing_user(user_service: UserService) -> None:
    from app.domains.identity.schemas import UserOIDCLogin

    first = await user_service.authenticate_oidc(
        UserOIDCLogin(provider="github", sub="gh-999", email="first@example.com"),
    )
    second = await user_service.authenticate_oidc(
        UserOIDCLogin(
            provider="github",
            sub="gh-999",
            email="should-ignore@example.com",
        ),
    )
    assert second.id == first.id
    assert second.email == "first@example.com"
