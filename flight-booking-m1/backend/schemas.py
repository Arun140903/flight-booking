from datetime import datetime
from pydantic import BaseModel
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