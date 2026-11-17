from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import UserRole
from app.database.session import get_db
from app.dependencies.auth import require_role
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "", response_model=schemas.BookingOut, status_code=status.HTTP_201_CREATED
)
def check_in(
    data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.VALET)),
):
    return booking_service.check_in(db, data, current_user)