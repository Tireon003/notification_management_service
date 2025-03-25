from uuid import UUID
from datetime import datetime as dt

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core import Base
from src.enums import ProcessingStatusEnum, CategoryEnum


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    title = mapped_column(String(256), nullable=False)
    text: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[dt] = mapped_column(default=dt.now())
    read_at: Mapped[dt | None] = mapped_column(nullable=True, default=None)
    category: Mapped[CategoryEnum | None] = mapped_column(
        nullable=True,
        default=None,
    )
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    processing_status: Mapped[ProcessingStatusEnum] = mapped_column(
        default="pending",
    )
