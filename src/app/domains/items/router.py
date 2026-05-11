from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.domains.identity.model import User
from app.domains.items.model import Item
from app.domains.items.repository import ItemRepository
from app.domains.items.schemas import ItemCreate, ItemResponse, ItemUpdate
from app.domains.items.service import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"],
    route_class=DishkaRoute,
)


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
) -> list[Item]:
    return await repo.list_public(skip=skip, limit=limit)


@router.get("/mine", response_model=list[ItemResponse])
async def list_my_items(
    current_user: FromDishka[User],
    repo: FromDishka[ItemRepository],
    skip: int = 0,
    limit: int = 100,
) -> list[Item]:
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
    current_user: FromDishka[User],
    svc: FromDishka[ItemService],
) -> Item:
    return await svc.update(item_id, data, owner_id=current_user.id)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    current_user: FromDishka[User],
    svc: FromDishka[ItemService],
) -> None:
    await svc.delete(item_id, owner_id=current_user.id)
