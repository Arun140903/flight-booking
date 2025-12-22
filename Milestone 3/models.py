from sqlalchemy import Column,Integer,String,DateTime,DECIMAL,ForeignKey
from .db import Base
from sqlalchemy.orm import relationship
from datetime import datetime
class Flight(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, index=True)
    flight_no = Column(String(10), nullable=False)
    airline_name = Column(String(50), nullable=False)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    base_fare = Column(DECIMAL(10, 2), nullable=False)
    total_seats = Column(Integer, nullable=False)
    seats_available = Column(Integer, nullable=False)
class FareHistory(Base):
    __tablename__ = "fare_history"
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    dynamic_price = Column(DECIMAL(10, 2), nullable=False)
    seats_available = Column(Integer, nullable=False)
    demand_level = Column(String(10), nullable=True)
    flight = relationship("Flight")
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    pnr = Column(String(12), unique=True, nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    seat_no = Column(String(5), nullable=True)
    price = Column(DECIMAL(10,2), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)    