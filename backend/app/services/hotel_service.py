from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.repositories import hotel_repository


def get_my_hotel(db: Session, user: models.User) -> models.Hotel:
    hotel = hotel_repository.get_by_id(db, user.hotel_id) if user.hotel_id else None
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found"
        )
    return hotel