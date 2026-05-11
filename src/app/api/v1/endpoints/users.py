from uuid import UUID

from dishka import FromDishka
from fastapi import APIRouter

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    repo: FromDishka[UserRepository],
    skip: int = 0,
    limit: int = 100,
):
    return await repo.list(skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: FromDishka[User]) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    svc: FromDishka[UserService],
) -> User:
    return await svc.get(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    svc: FromDishka[UserService],
) -> User:
    return await svc.update(user_id, data)
