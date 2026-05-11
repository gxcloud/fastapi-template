from uuid import UUID

from sqlalchemy import select

from app.common.base.repository import BaseRepository
from app.domains.identity.model import User


class UserRepository(BaseRepository[User]):
    model_class = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_ids(self, ids: list[UUID]) -> list[User]:
        stmt = select(User).where(User.id.in_(ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
