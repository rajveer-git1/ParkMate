from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import BookingStatus, UserRole
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_role
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


@router.post("/{booking_id}/checkout", response_model=schemas.BookingOut)
def check_out(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role(UserRole.HOTEL, UserRole.VALET)
    ),
):
    return booking_service.check_out(db, booking_id, current_user)


@router.get("", response_model=list[schemas.BookingDetail])
def list_bookings(
    booking_status: Optional[BookingStatus] = Query(None, alias="status"),
    lot_id: Optional[int] = None,
    search: Optional[str] = Query(None, max_length=50),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return booking_service.list_bookings(
        db,
        current_user,
        booking_status=booking_status,
        lot_id=lot_id,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/summary", response_model=schemas.BookingSummary)
def booking_summary(
    lot_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_role(UserRole.OWNER, UserRole.HOTEL)
    ),
):
    return booking_service.summary(db, current_user, lot_id)