from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.app import create_app
from app.models import Base
from app.repositories.item import ItemRepository
from app.repositories.user import UserRepository
from app.services.item import ItemService
from app.services.user import UserService


@pytest_asyncio.fixture(scope="session")
async def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="session")
async def db_url(postgres) -> str:
    return postgres.get_connection_url().replace("psycopg2", "asyncpg")


@pytest_asyncio.fixture(scope="session")
async def engine(db_url):
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def client(db_url) -> AsyncGenerator[AsyncClient, None]:
    import os
    os.environ["DB_URL"] = db_url
    os.environ["SECRET_KEY"] = "test-secret-key"

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    os.environ.pop("DB_URL", None)
    os.environ.pop("SECRET_KEY", None)


@pytest_asyncio.fixture
async def user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


@pytest_asyncio.fixture
async def item_repo(session: AsyncSession) -> ItemRepository:
    return ItemRepository(session=session)


@pytest_asyncio.fixture
async def user_service(user_repo: UserRepository) -> UserService:
    return UserService(repo=user_repo)


@pytest_asyncio.fixture
async def item_service(item_repo: ItemRepository) -> ItemService:
    return ItemService(repo=item_repo)


@pytest_asyncio.fixture
async def auth_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    data = response.json()
    return data["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}
