from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    users = relationship("User", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    hotel = relationship("Hotel", back_populates="users")
    lots = relationship("ParkingLot", back_populates="owner")
    bookings = relationship("Booking", back_populates="valet")


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    total_slots = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    owner = relationship("User", back_populates="lots")
    bookings = relationship("Booking", back_populates="lot")


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