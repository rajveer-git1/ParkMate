from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import UserRole
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_role
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register/owner",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_owner(data: schemas.OwnerRegister, db: Session = Depends(get_db)):
    return user_service.register_owner(db, data)


@router.post(
    "/register/hotel",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_hotel(data: schemas.HotelRegister, db: Session = Depends(get_db)):
    return user_service.register_hotel(db, data)


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return user_service.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post(
    "/valets",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_valet(
    data: schemas.ValetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(UserRole.HOTEL)),
):
    return user_service.create_valet(db, data, current_user)