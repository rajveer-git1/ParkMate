from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import LotStatus
from app.repositories import hotel_repository, lot_repository
from app.utils.geo import haversine_km, parse_coordinates


def _with_status(db: Session, lot: models.ParkingLot) -> dict:
    occupied = lot_repository.count_occupied(db, lot.id)
    data = schemas.LotOut.model_validate(lot).model_dump()
    data["occupied_slots"] = occupied
    data["available_slots"] = max(lot.total_slots - occupied, 0)
    data["status"] = (
        LotStatus.FULL.value if occupied >= lot.total_slots else LotStatus.AVAILABLE.value
    )
    return data


def create_lot(
    db: Session, data: schemas.LotCreate, owner: models.User
) -> models.ParkingLot:
    latitude, longitude = parse_coordinates(data.coordinates)
    lot = lot_repository.add(
        db,
        owner_id=owner.id,
        name=data.name,
        address=data.address,
        city=data.city,
        latitude=latitude,
        longitude=longitude,
        total_slots=data.total_slots,
        price_per_hour=data.price_per_hour,
    )
    db.commit()
    db.refresh(lot)
    return lot


def list_my_lots(db: Session, owner: models.User) -> list[dict]:
    lots = lot_repository.list_by_owner(db, owner.id)
    return [_with_status(db, lot) for lot in lots]


def update_lot(
    db: Session, lot_id: int, data: schemas.LotUpdate, owner: models.User
) -> models.ParkingLot:
    lot = lot_repository.get_by_id(db, lot_id)
    if lot is None or lot.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    changes = {
        key: value
        for key, value in data.model_dump(exclude_unset=True).items()
        if value is not None
    }

    occupied = lot_repository.count_occupied(db, lot.id)
    if "total_slots" in changes and changes["total_slots"] < occupied:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set slots below the {occupied} cars currently parked",
        )
    if changes.get("is_active") is False and occupied > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deactivate while {occupied} cars are parked here",
        )

    if "coordinates" in changes:
        lot.latitude, lot.longitude = parse_coordinates(changes.pop("coordinates"))

    for key, value in changes.items():
        setattr(lot, key, value)

    db.commit()
    db.refresh(lot)
    return lot


def nearby_lots(
    db: Session, user: models.User, radius_km: float, only_available: bool
) -> list[dict]:
    hotel = hotel_repository.get_by_id(db, user.hotel_id)
    if hotel is None or hotel.latitude is None or hotel.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your hotel has no coordinates set",
        )

    results = []
    for lot in lot_repository.list_active(db):
        if lot.latitude is None or lot.longitude is None:
            continue

        distance = haversine_km(
            hotel.latitude, hotel.longitude, lot.latitude, lot.longitude
        )
        if distance > radius_km:
            continue

        item = _with_status(db, lot)
        if only_available and item["status"] == LotStatus.FULL.value:
            continue

        item["distance_km"] = round(distance, 2)
        results.append(item)

    results.sort(key=lambda item: item["distance_km"])
    return results