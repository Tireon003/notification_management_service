from enum import Enum


class CategoryEnum(Enum):
    critical = "critical"
    warning = "warning"
    info = "info"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return bool(value in cls._value2member_map_)
