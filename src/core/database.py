import logging

from collections.abc import AsyncIterator, AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import Settings

logger = logging.getLogger(__name__)


class Database:

    _INSTANCE: Literal[None] | "Database" = None
    _INITIALIZED = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "Database":
        if cls._INSTANCE is None:
            cls._INSTANCE = super().__new__(cls)
        return cls._INSTANCE

    def __init__(self, settings: Settings) -> None:
        if not self._INITIALIZED:
            self._engine = create_async_engine(url=settings.db_url, echo=True)
            self._session_maker = async_sessionmaker(
                self._engine,
                expire_on_commit=False,
            )
            self._INITIALIZED = True

    @asynccontextmanager
    async def create_async_session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_maker() as session:
            yield session

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        try:
            async with self.create_async_session() as session:
                yield session
        except Exception as err:
            logger.error(
                f"Error occurred while creating async session: %s",
                str(err),
            )
            await session.rollback()
            raise err


class Base(DeclarativeBase):
    pass


def get_database(settings: Settings) -> Database:
    return Database(settings=settings)
