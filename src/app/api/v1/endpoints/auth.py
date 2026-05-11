from dishka import FromDishka
from fastapi import APIRouter

from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, svc: FromDishka[UserService]):
    return await svc.create(data)


@router.post("/login")
async def login(data: UserCreate, svc: FromDishka[UserService]):
    user = await svc.authenticate(data.email, data.password)
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}
