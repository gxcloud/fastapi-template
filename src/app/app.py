import logging

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.common.config import settings
from app.common.di import AppProvider
from app.common.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.common.health import router as health_router
from app.common.middleware import RequestLoggingMiddleware
from app.domains.identity.router import auth_router, user_router
from app.domains.items.router import router as items_router

logger = logging.getLogger(__name__)


def create_app(db_url: str | None = None) -> FastAPI:
    app = FastAPI(title="app", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    from fastapi import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]

    container = make_async_container(AppProvider(db_url=db_url))
    setup_dishka(container, app)

    @app.on_event("startup")
    async def validate_startup() -> None:
        from app.common.startup import check_database_connection

        try:
            await check_database_connection()
            logger.info("Database connection established")
        except Exception:  # noqa: BLE001
            logger.warning(
                "Database connection failed — app started without DB. "
                "Set DB_URL environment variable.",
            )

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await container.close()

    v1_router = APIRouter(prefix="/v1")
    v1_router.include_router(health_router)
    v1_router.include_router(auth_router)
    v1_router.include_router(user_router)
    v1_router.include_router(items_router)
    app.include_router(v1_router, prefix="/api")

    return app
