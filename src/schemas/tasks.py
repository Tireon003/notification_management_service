from pydantic import BaseModel, Field

from src.enums import CategoryEnum


class AnalyzeTextTaskResult(BaseModel):
    category: CategoryEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    keywords: list[str]
