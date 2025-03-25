import logging
from uuid import UUID
from datetime import datetime as dt

from src.exceptions import NotificationAlreadyReadError
from src.repositories import NotificationRepository
from src.schemas import (
    Paginator,
    NotificationRead,
    NotificationCreate,
    NotificationUpdate,
)

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    async def get_notifications(
        self,
        paginator: Paginator,
    ) -> list[NotificationRead]:
        notifications_orm = await self._repository.get_all(paginator)
        notifications_dto = [
            NotificationRead.model_validate(item) for item in notifications_orm
        ]
        return notifications_dto

    async def get_notification(
        self,
        notification_id: UUID,
    ) -> NotificationRead:
        notification_orm = await self._repository.get_one(notification_id)
        notification_dto = NotificationRead.model_validate(notification_orm)
        return notification_dto

    async def create_notification(
        self,
        notification_data: NotificationCreate,
    ) -> NotificationRead:
        new_notification = await self._repository.create(notification_data)
        new_notification_dto = NotificationRead.model_validate(
            new_notification
        )
        return new_notification_dto

    async def read_notification(
        self,
        notification_id: UUID,
    ) -> NotificationRead:
        notification_orm = await self._repository.get_one(notification_id)
        notification_dto = NotificationRead.model_validate(notification_orm)
        if notification_dto.read_at is not None:
            raise NotificationAlreadyReadError("Notification already read!")
        update_notification_dto = NotificationUpdate.model_validate(
            notification_dto
        )
        update_notification_dto.read_at = dt.now()
        updated_notification_orm = await self._repository.update(
            obj_id=notification_id,
            data_to_update=update_notification_dto,
        )
        updated_notification_dto = NotificationRead.model_validate(
            updated_notification_orm
        )
        return updated_notification_dto
