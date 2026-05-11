from functools import lru_cache

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.common.config import settings


@lru_cache(maxsize=1)
def get_engine():
    return create_async_engine(
        str(settings.db_url),
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )


def get_session_factory():
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)
