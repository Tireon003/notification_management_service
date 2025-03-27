from fastapi import APIRouter

from .notification import router as notifications_router
from .view import router as views_router

gateway_router = APIRouter()

gateway_router.include_router(notifications_router, prefix="/api")
gateway_router.include_router(views_router)

__all__ = ("gateway_router",)
