from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.common.config import settings

engine = create_async_engine(
    str(settings.db_url),
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
