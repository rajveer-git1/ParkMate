from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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