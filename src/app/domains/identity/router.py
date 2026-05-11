from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.common.security import create_access_token
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.identity.schemas import UserCreate, UserResponse, UserUpdate
from app.domains.identity.service import UserService

auth_router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)
user_router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, svc: FromDishka[UserService]) -> User:
    return await svc.create(data)


@auth_router.post("/login")
async def login(
    data: UserCreate,
    svc: FromDishka[UserService],
) -> dict[str, str]:
    user = await svc.authenticate(data.email, data.password)
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@user_router.get("", response_model=list[UserResponse])
async def list_users(
    repo: FromDishka[UserRepository],
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    return await repo.list(skip=skip, limit=limit)


@user_router.get("/me", response_model=UserResponse)
async def get_me(current_user: FromDishka[User]) -> User:
    return current_user


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    svc: FromDishka[UserService],
) -> User:
    return await svc.get(user_id)


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    svc: FromDishka[UserService],
) -> User:
    return await svc.update(user_id, data)
