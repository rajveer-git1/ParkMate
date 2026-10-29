from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.enums import UserRole
from app.repositories import hotel_repository, user_repository
from app.utils.geo import parse_coordinates
from app.utils.security import create_access_token, hash_password, verify_password


def _ensure_email_is_free(db: Session, email: str) -> None:
    if user_repository.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


def register_owner(db: Session, data: schemas.OwnerRegister) -> models.User:
    email = data.email.lower()
    _ensure_email_is_free(db, email)

    user = user_repository.add(
        db,
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.OWNER.value,
    )
    db.commit()
    db.refresh(user)
    return user


def register_hotel(db: Session, data: schemas.HotelRegister) -> models.User:
    email = data.email.lower()
    _ensure_email_is_free(db, email)

    latitude, longitude = parse_coordinates(data.hotel.coordinates)
    hotel = hotel_repository.add(
        db,
        name=data.hotel.name,
        address=data.hotel.address,
        city=data.hotel.city,
        latitude=latitude,
        longitude=longitude,
    )
    user = user_repository.add(
        db,
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.HOTEL.value,
        hotel_id=hotel.id,
    )
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> dict:
    user = user_repository.get_by_email(db, email.lower())
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    return {
        "access_token": create_access_token(user.id, user.role),
        "token_type": "bearer",
        "role": user.role,
    }


def create_valet(
    db: Session, data: schemas.ValetCreate, hotel_staff: models.User
) -> models.User:
    email = data.email.lower()
    _ensure_email_is_free(db, email)

    valet = user_repository.add(
        db,
        name=data.name,
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.VALET.value,
        hotel_id=hotel_staff.hotel_id,
    )
    db.commit()
    db.refresh(valet)
    return valet