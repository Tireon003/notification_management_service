from typing import AsyncGenerator
from uuid import uuid4
from datetime import datetime as dt
import pytest
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core import Database
from src.models import Notification
from src.repositories import NotificationRepository
from src.schemas import NotificationRead, NotificationCreate
from src.services import NotificationService


class MockSettings(Settings):

    @property
    def db_url(self) -> str:
        return "sqlite+aiosqlite:///test.db"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=".env_test")


@pytest.fixture
def settings() -> MockSettings:
    return MockSettings()


def get_mock_settings() -> MockSettings:
    return MockSettings()


@pytest.fixture
def app(settings: MockSettings) -> FastAPI:
    from src.main import create_app

    app = create_app(settings)
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    app.dependency_overrides[get_settings] = get_mock_settings
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def database(settings: MockSettings) -> Database:
    return Database(settings)


@pytest.fixture
async def test_notification(database: Database) -> NotificationRead:
    async with AsyncSession(database._engine) as session:
        notification_data = NotificationCreate(
            title="Info test message",
            text="This is a test message",
            user_id=uuid4(),
        )
        notification = Notification(
            id=uuid4(),
            created_at=dt.now(),
            **notification_data.model_dump(),
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        created_notification = NotificationRead.model_validate(notification)
        return created_notification


@pytest.fixture
async def notification_service(
    database: Database,
) -> AsyncGenerator[NotificationService, None]:
    async with database.create_async_session() as session:
        repo = NotificationRepository(session)
        service = NotificationService(repo)
        yield service
