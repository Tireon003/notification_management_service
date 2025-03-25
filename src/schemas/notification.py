from datetime import datetime as dt
from pydantic import BaseModel, UUID4, Field, ConfigDict


class BaseNotification(BaseModel):

    user_id: UUID4
    title: str = Field(..., max_length=256)
    text: str = Field(..., max_length=512)


class NotificationCreate(BaseNotification):
    pass


class NotificationRead(BaseNotification):
    id: UUID4
    created_at: dt
    read_at: dt | None = Field(default=None)
    category: str | None = Field(default=None)
    confidence: float | None = Field(default=None)
    processing_status: str | None = Field(default="pending")

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    title: str = Field(..., max_length=256)
    text: str = Field(..., max_length=512)
    read_at: dt | None = Field(default=None)
    category: str | None = Field(default=None)
    confidence: float | None = Field(default=None)
    processing_status: str | None = Field(default="pending")

    model_config = ConfigDict(extra="ignore", from_attributes=True)
