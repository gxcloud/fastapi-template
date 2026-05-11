from uuid import UUID

from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def create(self, data: UserCreate) -> User:
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self._repo.create(user)

    async def get(self, id: UUID) -> User:
        user = await self._repo.get(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def update(self, id: UUID, data: UserUpdate) -> User:
        user = await self.get(id)
        if data.email is not None:
            user.email = data.email
        if data.password is not None:
            user.hashed_password = hash_password(data.password)
        if data.is_active is not None:
            user.is_active = data.is_active
        return await self._repo.create(user)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return user
