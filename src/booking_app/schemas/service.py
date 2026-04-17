from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None


class ServiceRead(BaseModel):
    id: int
    name: str
    description: str | None
    duration_minutes: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
