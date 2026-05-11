from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str | None = Field(default=None, min_length=8)
    oidc_sub: str | None = None
    oidc_provider: str | None = None

    @model_validator(mode="after")
    def check_auth_method(self) -> "UserCreate":
        if not self.password and not (self.oidc_sub and self.oidc_provider):
            raise ValueError(
                "Either password or oidc_sub+oidc_provider must be provided",
            )
        if self.password and (self.oidc_sub or self.oidc_provider):
            raise ValueError(
                "Cannot provide both password and OIDC credentials",
            )
        return self


class UserOIDCLogin(BaseModel):
    provider: str
    sub: str
    email: EmailStr


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    oidc_sub: str | None
    oidc_provider: str | None

    model_config = {"from_attributes": True}
