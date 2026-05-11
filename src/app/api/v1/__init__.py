from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, items, users

router = APIRouter(prefix="/v1")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(items.router)
