from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI

from app.common.di import AppProvider
from app.common.health import router as health_router
from app.domains.identity.router import auth_router, user_router
from app.domains.items.router import router as items_router


def create_app(db_url: str | None = None) -> FastAPI:
    app = FastAPI(title="app", version="0.1.0")

    container = make_async_container(AppProvider(db_url=db_url))
    setup_dishka(container, app)

    v1_router = APIRouter(prefix="/v1")
    v1_router.include_router(health_router)
    v1_router.include_router(auth_router)
    v1_router.include_router(user_router)
    v1_router.include_router(items_router)
    app.include_router(v1_router, prefix="/api")

    return app
