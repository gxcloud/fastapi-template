from uuid import UUID

from fastapi import HTTPException, status

from app.domains.items.model import Item
from app.domains.items.repository import ItemRepository
from app.domains.items.schemas import ItemCreate, ItemUpdate


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

    async def update(self, id: UUID, data: ItemUpdate, owner_id: UUID) -> Item:
        item = await self.get(id)
        if item.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this item",
            )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(item, field, value)
        return await self._repo.create(item)

    async def delete(self, id: UUID, owner_id: UUID) -> None:
        item = await self.get(id)
        if item.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item",
            )
        await self._repo.delete(item)
