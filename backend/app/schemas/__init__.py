from app.schemas.auth import Token
from app.schemas.booking import BookingCreate, BookingOut
from app.schemas.hotel import HotelCreate, HotelOut
from app.schemas.lot import LotCreate, LotOut, LotUpdate, LotWithStatus, NearbyLot
from app.schemas.user import HotelRegister, OwnerRegister, UserOut, ValetCreate

__all__ = [
    "Token",
    "BookingCreate",
    "BookingOut",
    "HotelCreate",
    "HotelOut",
    "LotCreate",
    "LotOut",
    "HotelRegister",
    "OwnerRegister",
    "UserOut",
    "ValetCreate",
    "LotUpdate",
    "LotWithStatus",
    "NearbyLot",
]