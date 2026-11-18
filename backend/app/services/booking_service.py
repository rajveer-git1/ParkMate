from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import BookingStatus, UserRole
from app.repositories import booking_repository, lot_repository
from app.utils.billing import calculate_fee


def check_in(
    db: Session, data: schemas.BookingCreate, valet: models.User
) -> models.Booking:
    lot = lot_repository.get_by_id(db, data.lot_id)
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")
    if not lot.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This lot is not accepting cars",
        )

    if booking_repository.get_parked_by_vehicle(db, data.vehicle_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This vehicle is already parked",
        )

    occupied = lot_repository.count_occupied(db, lot.id)
    if occupied >= lot.total_slots:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This lot is full"
        )

    booking = booking_repository.add(
        db,
        hotel_id=valet.hotel_id,
        lot_id=lot.id,
        valet_id=valet.id,
        guest_name=data.guest_name,
        guest_phone=data.guest_phone,
        vehicle_number=data.vehicle_number,
        vehicle_model=data.vehicle_model,
        vehicle_color=data.vehicle_color,
        price_per_hour=lot.price_per_hour,
    )
    db.commit()
    db.refresh(booking)
    return booking


def check_out(db: Session, booking_id: int, user: models.User) -> models.Booking:
    booking = booking_repository.get_by_id(db, booking_id)
    if booking is None or booking.hotel_id != user.hotel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    if booking.status != BookingStatus.PARKED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This car has already been returned",
        )

    check_out_time = datetime.now()
    total_fee = calculate_fee(
        booking.check_in_time, check_out_time, booking.price_per_hour
    )
    booking_repository.mark_completed(
        db, booking, check_out_time=check_out_time, total_fee=total_fee
    )
    db.commit()
    db.refresh(booking)
    return booking


def _scope(user: models.User) -> dict:
    if user.role == UserRole.OWNER.value:
        return {"owner_id": user.id}
    return {"hotel_id": user.hotel_id}


def _to_detail(booking: models.Booking) -> dict:
    data = schemas.BookingOut.model_validate(booking).model_dump()
    data["lot_name"] = booking.lot.name
    data["hotel_name"] = booking.hotel.name
    data["valet_name"] = booking.valet.name
    return data


def list_bookings(
    db: Session,
    user: models.User,
    *,
    booking_status: Optional[BookingStatus],
    lot_id: Optional[int],
    search: Optional[str],
    limit: int,
    offset: int,
) -> list[dict]:
    if user.role == UserRole.VALET.value:
        booking_status = BookingStatus.PARKED

    search = search.strip() if search else None

    bookings = booking_repository.list_bookings(
        db,
        **_scope(user),
        booking_status=booking_status.value if booking_status else None,
        lot_id=lot_id,
        search=search or None,
        limit=limit,
        offset=offset,
    )
    return [_to_detail(booking) for booking in bookings]


def summary(db: Session, user: models.User, lot_id: Optional[int]) -> dict:
    return booking_repository.summarize(db, **_scope(user), lot_id=lot_id)