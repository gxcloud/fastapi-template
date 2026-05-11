from uuid import UUID

from fastapi import HTTPException, status

from app.common.security import generate_salt, hash_password, verify_password
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.identity.schemas import UserCreate, UserOIDCLogin, UserUpdate


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
        if data.oidc_sub and data.oidc_provider:
            existing_oidc = await self._repo.get_by_oidc(
                data.oidc_provider,
                data.oidc_sub,
            )
            if existing_oidc:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="OIDC account already linked",
                )
            user = User(
                email=data.email,
                oidc_sub=data.oidc_sub,
                oidc_provider=data.oidc_provider,
            )
        else:
            salt = generate_salt()
            user = User(
                email=data.email,
                hashed_password=hash_password(data.password, salt),
                password_salt=salt,
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
        if data.email is not None and data.email != user.email:
            existing = await self._repo.get_by_email(data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            user.email = data.email
        if data.password is not None:
            salt = generate_salt()
            user.hashed_password = hash_password(data.password, salt)
            user.password_salt = salt
        if data.is_active is not None:
            user.is_active = data.is_active
        return await self._repo.save(user)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._repo.get_by_email(email)
        if not user or not user.hashed_password or not user.password_salt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(password, user.hashed_password, user.password_salt):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return user

    async def authenticate_oidc(self, data: UserOIDCLogin) -> User:
        user = await self._repo.get_by_oidc(data.provider, data.sub)
        if user:
            return user
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered with different login method",
            )
        user = User(
            email=data.email,
            oidc_sub=data.sub,
            oidc_provider=data.provider,
        )
        return await self._repo.create(user)
