from collections.abc import AsyncIterable
from uuid import UUID

from dishka import Provider, Scope, from_context, provide
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.common.config import Settings, settings
from app.common.database import get_session_factory
from app.common.security import decode_access_token
from app.domains.identity.model import User
from app.domains.identity.repository import UserRepository
from app.domains.identity.service import UserService
from app.domains.items.repository import ItemRepository
from app.domains.items.service import ItemService


class AppProvider(Provider):
    request = from_context(Request, scope=Scope.REQUEST)

    def __init__(self, db_url: str | None = None) -> None:
        super().__init__()
        self._db_url = db_url

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        if self._db_url:
            engine = create_async_engine(self._db_url)
            factory = async_sessionmaker(engine, expire_on_commit=False)
        else:
            factory = get_session_factory()
        async with factory() as session:
            yield session
            await session.commit()

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def get_item_repo(self, session: AsyncSession) -> ItemRepository:
        return ItemRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def get_user_service(self, repo: UserRepository) -> UserService:
        return UserService(repo=repo)

    @provide(scope=Scope.REQUEST)
    def get_item_service(self, repo: ItemRepository) -> ItemService:
        return ItemService(repo=repo)

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        request: Request,
        repo: UserRepository,
    ) -> User:
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()
        user_id = decode_access_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        user = await repo.get(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
