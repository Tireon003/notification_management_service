from fastapi import APIRouter

from .notification import router as notifications_router

gateway_router = APIRouter(
    prefix="/api",
)

gateway_router.include_router(notifications_router)

__all__ = ("gateway_router",)
