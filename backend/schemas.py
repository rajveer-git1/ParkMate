from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.utils import parse_coordinates


# ---------- Hotel ----------
class HotelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    coordinates: str = Field(description="Copy from Google Maps, e.g. 19.0760, 72.8777")

    @field_validator("coordinates")
    @classmethod
    def check_coordinates(cls, value: str) -> str:
        parse_coordinates(value)
        return value


class HotelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime


# ---------- User ----------
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


# ---------- Parking lot ----------
class LotCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    coordinates: str = Field(description="Copy from Google Maps, e.g. 19.0760, 72.8777")
    total_slots: int = Field(gt=0)
    price_per_hour: float = Field(gt=0)

    @field_validator("coordinates")
    @classmethod
    def check_coordinates(cls, value: str) -> str:
        parse_coordinates(value)
        return value


class LotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_slots: int
    price_per_hour: float
    is_active: bool
    created_at: datetime


# ---------- Booking ----------
class BookingCreate(BaseModel):
    lot_id: int
    guest_name: str = Field(min_length=1, max_length=100)
    guest_phone: str = Field(min_length=5, max_length=20)
    vehicle_number: str = Field(min_length=1, max_length=20)
    vehicle_model: Optional[str] = None


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    lot_id: int
    valet_id: int
    guest_name: str
    guest_phone: str
    vehicle_number: str
    vehicle_model: Optional[str] = None
    price_per_hour: float
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    total_fee: Optional[float] = None
    status: str

    # ---------- Login ----------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str