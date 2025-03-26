from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings, Settings
from src.core import Database


def get_database(settings: Settings = Depends(get_settings)) -> Database:
    return Database(settings)


async def get_db_session(
    database: Database = Depends(get_database),
) -> AsyncGenerator[AsyncSession, None]:
    async with database.create_async_session() as session:
        yield session
