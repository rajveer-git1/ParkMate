from enum import Enum


class UserRole(str, Enum):
    OWNER = "owner"
    HOTEL = "hotel"
    VALET = "valet"


class BookingStatus(str, Enum):
    PARKED = "parked"
    COMPLETED = "completed"


class LotStatus(str, Enum):
    AVAILABLE = "Available"
    FULL = "Full"