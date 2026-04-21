from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..shared.enums import BookingStatus


class BookingCreate(BaseModel):
    user_id: int
    service_id: int
    start_time: datetime
    notes: str | None = None


class BookingRead(BaseModel):
    id: int
    user_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
