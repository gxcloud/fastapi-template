from fastapi import APIRouter
from sqlalchemy import text

from app.common.database import get_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:  # noqa: BLE001
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from None
