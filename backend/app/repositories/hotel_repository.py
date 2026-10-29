from sqlalchemy.orm import Session

from app.models import Hotel


def add(
    db: Session,
    *,
    name: str,
    address: str,
    city: str,
    latitude: float,
    longitude: float,
) -> Hotel:
    hotel = Hotel(
        name=name,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(hotel)
    db.flush()
    return hotel