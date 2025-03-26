from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from src.core import Database
from src.core import Base
from src.enums import ProcessingStatusEnum
from src.schemas import NotificationRead


@pytest.mark.usefixtures("client", "database", "test_notification")
class TestApi:

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
        client: AsyncClient,
        test_notification: NotificationRead,
    ) -> None:
        url = f"/api/notification/{test_notification.id}"
        response = await client.get(url)
        assert response.status_code == 200, response.json()
        assert NotificationRead(**response.json()) == test_notification

    async def test_read_notification(
        self,
        client: AsyncClient,
        test_notification: NotificationRead,
    ) -> None:
        url = f"/api/notification/{test_notification.id}/read"
        response = await client.patch(url)
        assert response.status_code == 200, response.json()
        assert response.json().get("read_at") != test_notification.model_dump()

    async def test_check_notification_status(
        self,
        client: AsyncClient,
        test_notification: NotificationRead,
    ) -> None:
        url = f"/api/notification/{test_notification.id}/processing_status"
        response = await client.get(url)
        assert response.status_code == 200, response.json()
        assert response.json().get("status") in list(
            ProcessingStatusEnum._value2member_map_
        )
