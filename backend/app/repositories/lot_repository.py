from typing import Optional

from sqlalchemy.orm import Session

from app.core.enums import BookingStatus
from app.models import Booking, ParkingLot


def add(
    db: Session,
    *,
    owner_id: int,
    name: str,
    address: str,
    city: str,
    latitude: float,
    longitude: float,
    total_slots: int,
    price_per_hour: float,
) -> ParkingLot:
    lot = ParkingLot(
        owner_id=owner_id,
        name=name,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
        total_slots=total_slots,
        price_per_hour=price_per_hour,
    )
    db.add(lot)
    db.flush()
    return lot


def get_by_id(db: Session, lot_id: int) -> Optional[ParkingLot]:
    return db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()


def list_by_owner(db: Session, owner_id: int) -> list[ParkingLot]:
    return (
        db.query(ParkingLot)
        .filter(ParkingLot.owner_id == owner_id)
        .order_by(ParkingLot.id)
        .all()
    )


def list_active(db: Session) -> list[ParkingLot]:
    return db.query(ParkingLot).filter(ParkingLot.is_active.is_(True)).all()


def count_occupied(db: Session, lot_id: int) -> int:
    return (
        db.query(Booking)
        .filter(
            Booking.lot_id == lot_id,
            Booking.status == BookingStatus.PARKED.value,
        )
        .count()
    )