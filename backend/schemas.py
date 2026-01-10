from datetime import datetime
from pydantic import BaseModel
from typing import Optional
class FlightOut(BaseModel):
    id: int
    flight_no: str
    airline_name: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    base_fare: float
    total_seats: int
    seats_available: int
    class Config:
        from_attributes = True
class FlightWithPriceOut(FlightOut):
    dynamic_price: float
class FareHistoryOut(BaseModel):
    recorded_at: datetime
    dynamic_price: float
    seats_available: int
    demand_level: Optional[str]
    class Config:
        from_attributes = True
class BookingRequest(BaseModel):
    flight_id: int
    passenger_name: str
    seat_no: Optional[str] = None
class BookingResponse(BaseModel):
    pnr: str
    flight_id: int
    passenger_name: str
    seat_no: Optional[str]
    price: float
    status: str
    class Config:
        from_attributes = True