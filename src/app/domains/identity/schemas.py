from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}
