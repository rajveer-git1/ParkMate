from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.geo import parse_coordinates


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