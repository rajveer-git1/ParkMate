from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import UserRole
from app.database.session import get_db
from app.dependencies.auth import require_role
from app.services import hotel_service

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("/me", response_model=schemas.HotelOut)
def my_hotel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role(UserRole.HOTEL, UserRole.VALET)
    ),
):
    return hotel_service.get_my_hotel(db, current_user)