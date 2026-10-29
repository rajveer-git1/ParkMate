from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    valet_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(20), nullable=False)
    vehicle_number = Column(String(20), nullable=False)
    vehicle_model = Column(String(50))
    price_per_hour = Column(Float, nullable=False)
    check_in_time = Column(DateTime, default=datetime.now)
    check_out_time = Column(DateTime, nullable=True)
    total_fee = Column(Float, nullable=True)
    status = Column(String(20), default="parked")

    hotel = relationship("Hotel", back_populates="bookings")
    lot = relationship("ParkingLot", back_populates="bookings")
    valet = relationship("User", back_populates="bookings")