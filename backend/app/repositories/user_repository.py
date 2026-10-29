from typing import Optional

from sqlalchemy.orm import Session

from app.models import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def add(
    db: Session,
    *,
    name: str,
    email: str,
    phone: Optional[str],
    password_hash: str,
    role: str,
    hotel_id: Optional[int] = None,
) -> User:
    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=role,
        hotel_id=hotel_id,
    )
    db.add(user)
    db.flush()
    return user