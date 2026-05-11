from uuid import UUID

from dishka import FromDishka
from fastapi import APIRouter

from app.models.item import Item
from app.models.user import User
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    data: ItemCreate,
    current_user: FromDishka[User],
    svc: FromDishka[ItemService],
) -> Item:
    return await svc.create(data, owner_id=current_user.id)


@router.get("", response_model=list[ItemResponse])
async def list_items(
    repo: FromDishka[ItemRepository],
    skip: int = 0,
    limit: int = 100,
):
    return await repo.list_public(skip=skip, limit=limit)


@router.get("/mine", response_model=list[ItemResponse])
async def list_my_items(
    current_user: FromDishka[User],
    repo: FromDishka[ItemRepository],
    skip: int = 0,
    limit: int = 100,
):
    return await repo.list_by_owner(current_user.id, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    svc: FromDishka[ItemService],
) -> Item:
    return await svc.get(item_id)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    svc: FromDishka[ItemService],
) -> Item:
    return await svc.update(item_id, data)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    svc: FromDishka[ItemService],
) -> None:
    await svc.delete(item_id)
