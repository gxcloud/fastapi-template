from uuid import UUID

from pydantic import BaseModel


class ItemCreate(BaseModel):
    title: str
    description: str | None = None
    is_public: bool = False


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None


class ItemResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_public: bool
    owner_id: UUID

    model_config = {"from_attributes": True}
