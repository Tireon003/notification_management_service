from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.core import get_database
from src.repositories import NotificationRepository
from src.services.notification import NotificationService

settings = Settings()
db = get_database(settings)


async def notification_service(
    db_session: AsyncSession = Depends(db.get_async_session),
) -> NotificationService:
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)
    return service
