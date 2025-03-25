from pydantic import BaseModel, NonNegativeInt, Field


class Paginator(BaseModel):
    offset: NonNegativeInt | None = Field(default=None)
    limit: NonNegativeInt | None = Field(default=None)
