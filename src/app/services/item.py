from uuid import UUID

from fastapi import HTTPException, status

from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repo: ItemRepository) -> None:
        self._repo = repo

    async def create(self, data: ItemCreate, owner_id: UUID) -> Item:
        item = Item(**data.model_dump(), owner_id=owner_id)
        return await self._repo.create(item)

    async def get(self, id: UUID) -> Item:
        item = await self._repo.get(id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return item

    async def update(self, id: UUID, data: ItemUpdate) -> Item:
        item = await self.get(id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(item, field, value)
        return await self._repo.create(item)

    async def delete(self, id: UUID) -> None:
        item = await self.get(id)
        await self._repo.delete(item)
