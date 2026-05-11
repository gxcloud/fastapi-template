from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.di import AppProvider


def create_app() -> FastAPI:
    app = FastAPI(title="app", version="0.1.0")
    container = make_async_container(AppProvider())
    setup_dishka(container, app)
    app.include_router(v1_router, prefix="/api")
    return app
