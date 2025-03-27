import uuid
from datetime import datetime as dt, timedelta as td
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Notification
from src.schemas import Paginator, NotificationCreate, NotificationUpdate


class NotificationRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, obj_id: UUID) -> Notification:
        obj = await self._session.get_one(Notification, obj_id)
        return obj

    async def get_all(self, paginator: Paginator) -> list[Notification]:
        stmt = select(Notification).order_by(Notification.created_at.desc())
        if paginator.offset is not None:
            stmt = stmt.offset(paginator.offset)
        if paginator.limit is not None:
            stmt = stmt.limit(paginator.limit)
        result = await self._session.scalars(stmt)
        obj_list = [obj for obj in result.all()]
        return obj_list

    async def create(self, obj: NotificationCreate) -> Notification:
        odb_uuid = uuid.uuid4()
        new_obj = Notification(
            id=odb_uuid,
            created_at=dt.now(),
            **obj.model_dump(),
        )
        self._session.add(new_obj)
        await self._session.flush()
        await self._session.refresh(new_obj)
        await self._session.commit()
        return new_obj

    async def update(
        self,
        obj_id: UUID,
        data_to_update: NotificationUpdate,
    ) -> Notification:
        obj = await self._session.get_one(Notification, obj_id)

        # probably hardcode, I don't know how to do it else
        obj.title = data_to_update.title
        obj.text = data_to_update.text
        obj.confidence = data_to_update.confidence
        obj.category = data_to_update.category  # type: ignore[assignment]
        obj.read_at = data_to_update.read_at
        obj.processing_status = data_to_update.processing_status  # type: ignore[assignment]

        await self._session.commit()
        return obj
