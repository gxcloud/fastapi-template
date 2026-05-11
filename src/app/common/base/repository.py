from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base.model import Base


class BaseRepository[M: Base]:
    model_class: type[M] = None  # type: ignore[assignment]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, model: M) -> M:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def get(self, id: UUID) -> M | None:
        return await self._session.get(self.model_class, id)

    async def list(self, *, skip: int = 0, limit: int = 100) -> list[M]:
        stmt = select(self.model_class).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, model: M) -> None:
        await self._session.delete(model)
        await self._session.flush()
