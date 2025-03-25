from enum import Enum


class ProcessingStatusEnum(Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return bool(value in cls._value2member_map_)
