from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectPlaceCreate(BaseModel):
    external_id: int = Field(..., gt=0, description="Artwork ID from Art Institute API (must be positive)")


class ProjectPlaceUpdate(BaseModel):
    notes: str | None = Field(default=None)
    is_visited: bool | None = None


class ProjectPlaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    image_url: str | None
    notes: str | None
    is_visited: bool
    created_at: datetime
    updated_at: datetime
