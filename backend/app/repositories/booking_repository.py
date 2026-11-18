from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.enums import BookingStatus
from app.models import Booking, ParkingLot


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


def _filtered_query(
    db: Session,
    *,
    hotel_id: Optional[int],
    owner_id: Optional[int],
    booking_status: Optional[str],
    lot_id: Optional[int],
    search: Optional[str],
):
    query = db.query(Booking)

    if owner_id is not None:
        query = query.join(ParkingLot, Booking.lot_id == ParkingLot.id).filter(
            ParkingLot.owner_id == owner_id
        )
    if hotel_id is not None:
        query = query.filter(Booking.hotel_id == hotel_id)
    if booking_status is not None:
        query = query.filter(Booking.status == booking_status)
    if lot_id is not None:
        query = query.filter(Booking.lot_id == lot_id)
    if search:
        plate = search.upper().replace(" ", "").replace("-", "")
        query = query.filter(
            or_(
                Booking.vehicle_number.ilike(f"%{plate}%"),
                Booking.guest_name.ilike(f"%{search}%"),
            )
        )
    return query


def list_bookings(
    db: Session,
    *,
    hotel_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    booking_status: Optional[str] = None,
    lot_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Booking]:
    query = _filtered_query(
        db,
        hotel_id=hotel_id,
        owner_id=owner_id,
        booking_status=booking_status,
        lot_id=lot_id,
        search=search,
    )
    return (
        query.options(
            joinedload(Booking.lot),
            joinedload(Booking.hotel),
            joinedload(Booking.valet),
        )
        .order_by(Booking.check_in_time.desc(), Booking.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def summarize(
    db: Session,
    *,
    hotel_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    lot_id: Optional[int] = None,
) -> dict:
    query = _filtered_query(
        db,
        hotel_id=hotel_id,
        owner_id=owner_id,
        booking_status=None,
        lot_id=lot_id,
        search=None,
    )
    completed_query = query.filter(Booking.status == BookingStatus.COMPLETED.value)

    total_fees = completed_query.with_entities(
        func.coalesce(func.sum(Booking.total_fee), 0.0)
    ).scalar()

    return {
        "total_bookings": query.count(),
        "parked_now": query.filter(
            Booking.status == BookingStatus.PARKED.value
        ).count(),
        "completed": completed_query.count(),
        "total_fees": round(total_fees, 2),
    }