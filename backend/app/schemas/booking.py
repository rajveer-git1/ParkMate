from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookingCreate(BaseModel):
    lot_id: int
    guest_name: str = Field(min_length=1, max_length=100)
    guest_phone: str = Field(min_length=5, max_length=20)
    vehicle_number: str = Field(min_length=1, max_length=20)
    vehicle_model: Optional[str] = Field(default=None, max_length=50)
    vehicle_color: Optional[str] = Field(default=None, max_length=30)

    @field_validator("vehicle_number")
    @classmethod
    def clean_vehicle_number(cls, value: str) -> str:
        cleaned = value.upper().replace(" ", "").replace("-", "")
        if not cleaned:
            raise ValueError("Vehicle number cannot be empty")
        return cleaned

    @field_validator("vehicle_model", "vehicle_color")
    @classmethod
    def blank_to_none(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


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
    vehicle_color: Optional[str] = None
    price_per_hour: float
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    total_fee: Optional[float] = None
    status: str


class BookingDetail(BookingOut):
    lot_name: str
    hotel_name: str
    valet_name: str


class BookingSummary(BaseModel):
    total_bookings: int
    parked_now: int
    completed: int
    total_fees: float