import asyncio
import random
from typing import Any

from celery import Celery
from celery.app.task import Task
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from src.config import Settings
from src.enums import CategoryEnum, ProcessingStatusEnum
from src.models import Notification
from src.schemas import (
    AnalyzeTextTaskResult,
)

Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore[attr-defined]

settings = Settings()

# SQLAlchemy configuration for sync execution in celery
sync_driver_pg_url = settings.db_url.replace("asyncpg", "psycopg2")
engine = create_engine(sync_driver_pg_url)
session_maker = sessionmaker(engine)

celery = Celery(
    main=__name__,
    broker=f"{settings.redis_url}/1",
    backend=f"{settings.redis_url}/1",
)


@celery.task
def process_text(notification_id: str, text: str) -> None:
    set_notification_status(notification_id, ProcessingStatusEnum.processing)
    try:
        result = asyncio.run(analyze_text(text))
        set_notification_status(
            notification_id,
            ProcessingStatusEnum.completed,
        )
        set_notification_analysed_data(notification_id, result)

    except Exception as e:
        set_notification_status(notification_id, ProcessingStatusEnum.failed)


async def analyze_text(text: str) -> AnalyzeTextTaskResult:
    """
    Имитация работы AI API с задержкой 1-3 секунды
    """

    await asyncio.sleep(random.uniform(1, 3))
    # Простая логика категоризации на основе ключевых слов
    if any(word in text.lower() for word in ["error", "exception", "failed"]):
        category = CategoryEnum.critical.value
        confidence = random.uniform(0.7, 0.95)
    elif any(
        word in text.lower() for word in ["warning", "attention", "careful"]
    ):
        category = CategoryEnum.warning.value
        confidence = random.uniform(0.6, 0.9)
    else:
        category = CategoryEnum.info.value
        confidence = random.uniform(0.8, 0.99)

    return AnalyzeTextTaskResult(
        category=category,
        confidence=confidence,
        keywords=random.sample(text.split(), min(3, len(text.split()))),
    )


def set_notification_status(
    notification_id: str,
    status: ProcessingStatusEnum,
) -> None:
    with session_maker() as session:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(processing_status=status.value)
        )

        session.execute(stmt)
        session.commit()


def set_notification_analysed_data(
    notification_id: str,
    result_data: AnalyzeTextTaskResult,
) -> None:
    with session_maker() as session:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(
                confidence=result_data.confidence,
                category=result_data.category,
            )
        )

        session.execute(stmt)
        session.commit()
