from typing import TYPE_CHECKING
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator



if TYPE_CHECKING:
    from app.schemas.project_place import ProjectPlaceRead


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None)
    start_date: date | None = None
    place_external_ids: list[int] = Field(
        default_factory=list, description="List of artwork IDs from Art Institute API"
    )

    @field_validator("place_external_ids")
    @classmethod
    def validate_external_ids(cls, v: list[int]) -> list[int]:
        if any(id <= 0 for id in v):
            raise ValueError("All external_ids must be positive integers")
        return v


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    start_date: date | None
    status: str
    created_at: datetime
    updated_at: datetime
    places: list["ProjectPlaceRead"] = []


from app.schemas.project_place import ProjectPlaceRead

ProjectRead.model_rebuild()
