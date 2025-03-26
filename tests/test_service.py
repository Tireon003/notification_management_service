from typing import AsyncGenerator

import pytest

from src.core import Database
from src.core import Base
from src.schemas import NotificationRead
from src.services import NotificationService


@pytest.mark.usefixtures(
    "database",
    "test_notification",
    "notification_service",
)
class TestService:

    @pytest.fixture(autouse=True, scope="function")
    async def _setup(self, database: Database) -> AsyncGenerator[None, None]:
        async with database._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        yield

        async with database._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def test_get_notification(
        self,
        notification_service: NotificationService,
        test_notification: NotificationRead,
    ) -> None:
        notification = await notification_service.get_notification(
            test_notification.id
        )
        assert notification == test_notification

    async def test_read_notification(
        self,
        notification_service: NotificationService,
        test_notification: NotificationRead,
    ) -> None:
        notification = await notification_service.read_notification(
            test_notification.id
        )
        assert notification.read_at is not None
