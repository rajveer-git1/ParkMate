from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_role,
    verify_password,
)
from backend.database import get_db
from backend.utils import parse_coordinates

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


@router.post(
    "/register/owner",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_owner(data: schemas.OwnerRegister, db: Session = Depends(get_db)):
    email = data.email.lower()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/register/hotel",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_hotel(data: schemas.HotelRegister, db: Session = Depends(get_db)):
    email = data.email.lower()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    latitude, longitude = parse_coordinates(data.hotel.coordinates)
    hotel = models.Hotel(
        name=data.hotel.name,
        address=data.hotel.address,
        city=data.hotel.city,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(hotel)
    db.flush()

    user = models.User(
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="hotel",
        hotel_id=hotel.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username.lower())
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "role": user.role,
    }


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
    current_user: models.User = Depends(require_role("hotel")),
):
    email = data.email.lower()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    valet = models.User(
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="valet",
        hotel_id=current_user.hotel_id,
    )
    db.add(valet)
    db.commit()
    db.refresh(valet)
    return valet