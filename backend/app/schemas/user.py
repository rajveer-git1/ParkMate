from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.hotel import HotelCreate


class UserRegisterBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(min_length=6, max_length=72)


class OwnerRegister(UserRegisterBase):
    pass


class ValetCreate(UserRegisterBase):
    pass


class HotelRegister(UserRegisterBase):
    hotel: HotelCreate


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    hotel_id: Optional[int] = None
    is_active: bool
    created_at: datetime