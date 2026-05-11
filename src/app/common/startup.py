from sqlalchemy import text

from app.common.database import get_session_factory


async def check_database_connection() -> bool:
    factory = get_session_factory()
    async with factory() as session:
        await session.execute(text("SELECT 1"))
        return True
