from datetime import datetime,date
from typing import List,Literal
from fastapi import FastAPI,Depends,HTTPException,Query
from sqlalchemy import select,asc,desc
from sqlalchemy.orm import Session
from .db import get_db
from .models import Flight
from .schemas import FlightOut
app = FastAPI(
    title="Flight Booking Simulator - Milestone 1",
    description="Core flight search & data management APIs",
    version="1.0.0",
)
#     Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Milestone 1 backend running",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }
#     Retrieve ALL flights (with sorting)
@app.get("/api/flights", response_model=List[FlightOut])
def get_all_flights(
    sort_by: Literal["price", "duration"] = Query("price"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
):
    query = select(Flight)
    if sort_by == "price":
        order_column = Flight.base_fare
    else:
        order_column = Flight.duration_minutes
    if sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    flights = db.scalars(query).all()
    return flights
#      Search by origin, destination, date
@app.get("/api/flights/search", response_model=List[FlightOut])
def search_flights(
    origin: str = Query(..., description="Origin city (e.g., Mumbai)"),
    destination: str = Query(..., description="Destination city (e.g., Delhi)"),
    travel_date: date = Query(..., description="Travel date in YYYY-MM-DD"),
    sort_by: Literal["price", "duration"] = Query("price"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    ):
    origin_norm = origin.strip().title()
    dest_norm = destination.strip().title()
    if origin_norm == dest_norm:
        raise HTTPException(status_code=400, detail="Origin and destination must be different")
    start_dt = datetime.combine(travel_date, datetime.min.time())
    end_dt = datetime.combine(travel_date, datetime.max.time())
    query = (select(Flight).where(Flight.origin == origin_norm).where(Flight.destination == dest_norm).where(Flight.departure_time >= start_dt).where(Flight.departure_time <= end_dt))
    if sort_by == "price":
        order_column = Flight.base_fare
    else:
        order_column = Flight.duration_minutes
    if sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    flights = db.scalars(query).all()
    if not flights:
        raise HTTPException(status_code=404,detail=f"No flights found from {origin_norm} to {dest_norm} on {travel_date}",)
    return flights
#     Simulated external airline schedule API
@app.get("/api/external/mock-schedule")
def mock_airline_schedule():
    return {
        "provider": "Arun",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "flights": [
            {
                "flight_no": "FB401",
                "airline_name": "AirIndiaExpress",
                "origin": "Kolkata",
                "destination": "Chennai",
                "departure_time": "2025-11-25 06:00:00",
                "arrival_time": "2025-11-25 08:10:00",
                "duration_minutes": 130,
                "base_fare": 6425.00,
                "total_seats": 180,
                "seats_available": 100,
            },
            {
                "flight_no": "FB402",
                "airline_name": "AirIndiaExpress",
                "origin": "Hyderabad",
                "destination": "Mumbai",
                "departure_time": "2025-11-25 09:30:00",
                "arrival_time": "2025-11-25 12:05:00",
                "duration_minutes": 155,
                "base_fare": 6670.00,
                "total_seats": 120,
                "seats_available": 67,
                },],}