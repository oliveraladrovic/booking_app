from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
