from uuid import UUID

from sqlalchemy import select

from app.common.base.repository import BaseRepository
from app.domains.items.model import Item


class ItemRepository(BaseRepository[Item]):
    model_class = Item

    async def list_by_owner(
        self,
        owner_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_public(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.is_public.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
