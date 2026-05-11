---
name: fastapi-domain
description: Create a new domain/bounded context in the FastAPI domain-driven project
---

## Creating a New Domain

Each domain is a self-contained bounded context under `src/app/domains/<name>/`. Create these files:

```
src/app/domains/<name>/
├── __init__.py        # empty
├── model.py           # SQLAlchemy ORM model(s)
├── schemas.py         # Pydantic request/response models
├── repository.py      # Data access (extends BaseRepository)
├── service.py         # Business logic with HTTPException errors
└── router.py          # FastAPI endpoints (uses DishkaRoute)
```

## Step-by-Step

### 1. Model (`model.py`)

Extend `Base`, `UUIDMixin`, `TimestampMixin` from `app.common.base.model`:

```python
from uuid import UUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.common.base.model import Base, TimestampMixin, UUIDMixin

class MyModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "my_models"
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
```

### 2. Schemas (`schemas.py`)

Pydantic v2 with `from_attributes = True` for ORM mode:

```python
from pydantic import BaseModel

class MyModelCreate(BaseModel):
    name: str

class MyModelResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    model_config = {"from_attributes": True}
```

### 3. Repository (`repository.py`)

Extend `BaseRepository[ModelType]`, define `model_class`:

```python
from app.common.base.repository import BaseRepository
from app.domains.<name>.model import MyModel

class MyModelRepository(BaseRepository[MyModel]):
    model_class = MyModel

    async def find_by_owner(self, owner_id: UUID) -> list[MyModel]:
        stmt = select(MyModel).where(MyModel.owner_id == owner_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
```

### 4. Service (`service.py`)

Business logic with HTTPException for errors, ownership checks:

```python
from fastapi import HTTPException, status

class MyModelService:
    def __init__(self, repo: MyModelRepository) -> None:
        self._repo = repo

    async def create(self, data: MyModelCreate, owner_id: UUID) -> MyModel:
        model = MyModel(**data.model_dump(), owner_id=owner_id)
        return await self._repo.save(model)

    async def update(self, id: UUID, data: MyModelUpdate, owner_id: UUID) -> MyModel:
        model = await self._repo.get(id)
        if not model:
            raise HTTPException(404)
        if model.owner_id != owner_id:
            raise HTTPException(403, "Not authorized")
        ...
        return await self._repo.save(model)
```

### 5. Router (`router.py`)

Use `DishkaRoute` as route_class to enable `FromDishka` injection:

```python
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from app.domains.identity.model import User

router = APIRouter(prefix="/<name>", tags=["<name>"], route_class=DishkaRoute)

@router.post("", response_model=MyModelResponse, status_code=201)
async def create(
    data: MyModelCreate,
    current_user: FromDishka[User],
    svc: FromDishka[MyModelService],
):
    return await svc.create(data, owner_id=current_user.id)
```

### 6. Wire DI (`common/di.py`)

Add providers in `AppProvider`:

```python
from app.domains.<name>.repository import MyModelRepository
from app.domains.<name>.service import MyModelService

@provide(scope=Scope.REQUEST)
def get_<name>_repo(self, session: AsyncSession) -> MyModelRepository:
    return MyModelRepository(session=session)

@provide(scope=Scope.REQUEST)
def get_<name>_service(self, repo: MyModelRepository) -> MyModelService:
    return MyModelService(repo=repo)
```

### 7. Register Router (`app.py`)

Import and include the router in `create_app()`:

```python
from app.domains.<name>.router import router as <name>_router
v1_router.include_router(<name>_router)
```

### 8. Migration

```bash
uv run alembic revision --autogenerate -m "create <name> table"
```

### 9. Tests

Create `tests/domains/<name>/` with three files:
- `test_<name>.py` — API-level tests via `AsyncClient` and `auth_headers`
- `test_repository.py` — data access tests, needs `user_repo` for FK setup
- `test_service.py` — business logic tests including ownership enforcement

See `fastapi-test` skill for detailed patterns.
