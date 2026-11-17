from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.enums import BookingStatus
from app.models import Booking


def add(
    db: Session,
    *,
    hotel_id: int,
    lot_id: int,
    valet_id: int,
    guest_name: str,
    guest_phone: str,
    vehicle_number: str,
    vehicle_model: Optional[str],
    vehicle_color: Optional[str],
    price_per_hour: float,
) -> Booking:
    booking = Booking(
        hotel_id=hotel_id,
        lot_id=lot_id,
        valet_id=valet_id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        vehicle_number=vehicle_number,
        vehicle_model=vehicle_model,
        vehicle_color=vehicle_color,
        price_per_hour=price_per_hour,
        status=BookingStatus.PARKED.value,
    )
    db.add(booking)
    db.flush()
    return booking


def get_parked_by_vehicle(db: Session, vehicle_number: str) -> Optional[Booking]:
    return (
        db.query(Booking)
        .filter(
            Booking.vehicle_number == vehicle_number,
            Booking.status == BookingStatus.PARKED.value,
        )
        .first()
    )


def get_by_id(db: Session, booking_id: int) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.id == booking_id).first()


def mark_completed(
    db: Session, booking: Booking, *, check_out_time: datetime, total_fee: float
) -> Booking:
    booking.check_out_time = check_out_time
    booking.total_fee = total_fee
    booking.status = BookingStatus.COMPLETED.value
    db.flush()
    return booking