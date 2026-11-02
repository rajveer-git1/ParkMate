from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import UserRole
from app.database.session import get_db
from app.dependencies.auth import require_role
from app.services import lot_service

router = APIRouter(prefix="/lots", tags=["Parking Lots"])


@router.post("", response_model=schemas.LotOut, status_code=status.HTTP_201_CREATED)
def create_lot(
    data: schemas.LotCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.OWNER)),
):
    return lot_service.create_lot(db, data, current_user)


@router.get("/mine", response_model=list[schemas.LotWithStatus])
def my_lots(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.OWNER)),
):
    return lot_service.list_my_lots(db, current_user)


@router.get("/nearby", response_model=list[schemas.NearbyLot])
def nearby_lots(
    radius_km: float = Query(10, gt=0, le=200),
    only_available: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.HOTEL, UserRole.VALET)),
):
    return lot_service.nearby_lots(db, current_user, radius_km, only_available)


@router.put("/{lot_id}", response_model=schemas.LotOut)
def update_lot(
    lot_id: int,
    data: schemas.LotUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.OWNER)),
):
    return lot_service.update_lot(db, lot_id, data, current_user)