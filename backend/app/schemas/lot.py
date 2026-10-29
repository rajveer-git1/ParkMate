from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.geo import parse_coordinates


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