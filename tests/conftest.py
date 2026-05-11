from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer


@pytest_asyncio.fixture
async def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture
async def db_url(postgres) -> str:
    return postgres.get_connection_url().replace("psycopg2", "asyncpg")


@pytest_asyncio.fixture
async def engine(db_url):
    from app.common.base.model import Base

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
async def client(db_url, engine) -> AsyncGenerator[AsyncClient, None]:  # noqa: ARG001
    from app.app import create_app

    app = create_app(db_url=db_url)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def user_repo(session: AsyncSession):
    from app.domains.identity.repository import UserRepository

    return UserRepository(session=session)


@pytest_asyncio.fixture
async def item_repo(session: AsyncSession):
    from app.domains.items.repository import ItemRepository

    return ItemRepository(session=session)


@pytest_asyncio.fixture
async def user_service(user_repo):
    from app.domains.identity.service import UserService

    return UserService(repo=user_repo)


@pytest_asyncio.fixture
async def item_service(item_repo):
    from app.domains.items.service import ItemService

    return ItemService(repo=item_repo)


@pytest_asyncio.fixture
async def auth_token(client) -> str:
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
