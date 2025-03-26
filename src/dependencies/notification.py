from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.shared import get_db_session
from src.repositories import NotificationRepository
from src.services.notification import NotificationService


async def notification_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)
    return service
