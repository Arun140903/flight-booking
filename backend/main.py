from datetime import datetime,date
from typing import List,Literal
from fastapi import FastAPI,Depends,HTTPException,Query
from sqlalchemy import select,asc,desc
from sqlalchemy.orm import Session
from .db import get_db
from .models import Flight,FareHistory,Booking
from .schemas import FlightOut,FlightWithPriceOut,FareHistoryOut,BookingRequest,BookingResponse
from .dynamic_pricing import calculate_dynamic_price
import asyncio
import random
from .db import SessionLocal
from .utils import generate_pnr
from fastapi.middleware.cors import CORSMiddleware
from .db import engine
from .models import Base
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Flight Booking Simulator",
    description="Core flight search & data management APIs",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#     Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend running",
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
@app.get("/api/flights/search", response_model=List[FlightWithPriceOut])
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
    flights = db.scalars(query).all()
    if not flights:
        raise HTTPException(status_code=404,detail=f"No flights found from {origin_norm} to {dest_norm} on {travel_date}",)
    result_with_prices: List[FlightWithPriceOut] = []
    for f in flights:
        dyn_price = calculate_dynamic_price(
            base_fare=float(f.base_fare),
            seats_available=f.seats_available,
            total_seats=f.total_seats,
            departure_time=f.departure_time,
            airline_name=f.airline_name,
            demand_level=getattr(f, "demand_level", None),)
        result_with_prices.append(
            FlightWithPriceOut(
                id=f.id,
                flight_no=f.flight_no,
                airline_name=f.airline_name,
                origin=f.origin,
                destination=f.destination,
                departure_time=f.departure_time,
                arrival_time=f.arrival_time,
                duration_minutes=f.duration_minutes,
                base_fare=float(f.base_fare),
                total_seats=f.total_seats,
                seats_available=f.seats_available,
                dynamic_price=dyn_price,))
    reverse = sort_order == "desc"
    if sort_by == "price":
        result_with_prices.sort(key=lambda x: x.dynamic_price, reverse=reverse)
    else:
        result_with_prices.sort(key=lambda x: x.duration_minutes, reverse=reverse)
    return result_with_prices
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
#       Dynamic price endpoint for a single flight
@app.get("/api/flights/{flight_id}/price", response_model=FlightWithPriceOut)
def get_dynamic_price_for_flight(
    flight_id: int,
    db: Session = Depends(get_db),
):
    f = db.get(Flight, flight_id)
    if not f:
        raise HTTPException(status_code=404, detail=f"Flight with ID {flight_id} not found")
    dyn_price = calculate_dynamic_price(
        base_fare=float(f.base_fare),
        seats_available=f.seats_available,
        total_seats=f.total_seats,
        departure_time=f.departure_time,
        airline_name=f.airline_name,
        demand_level=getattr(f, "demand_level", None),)
    return FlightWithPriceOut(
        id=f.id,
        flight_no=f.flight_no,
        airline_name=f.airline_name,
        origin=f.origin,
        destination=f.destination,
        departure_time=f.departure_time,
        arrival_time=f.arrival_time,
        duration_minutes=f.duration_minutes,
        base_fare=float(f.base_fare),
        total_seats=f.total_seats,
        seats_available=f.seats_available,
        dynamic_price=dyn_price,)
#        Fare History Endpoint
@app.get("/api/flights/{flight_id}/history", response_model=list[FareHistoryOut])
def get_fare_history(flight_id: int, db: Session = Depends(get_db)):
    history = (db.query(FareHistory).filter(FareHistory.flight_id == flight_id).order_by(FareHistory.recorded_at.desc()).all())
    if not history:
        raise HTTPException(status_code=404, detail="No fare history recorded for this flight.")
    return history
#        Booking Endpoint (Concurrency Safety)    
@app.post("/api/bookings", response_model=BookingResponse)
def create_booking(request: BookingRequest, db: Session = Depends(get_db)):
    try:
        flight = (db.query(Flight).filter(Flight.id == request.flight_id).with_for_update().first())
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        if flight.seats_available <= 0:
            raise HTTPException(status_code=400, detail="No seats available")
        flight.seats_available -= 1
        final_price = calculate_dynamic_price(
            base_fare=float(flight.base_fare),
            seats_available=flight.seats_available,
            total_seats=flight.total_seats,
            departure_time=flight.departure_time,
            airline_name=flight.airline_name,)
        booking = Booking(
            pnr=generate_pnr(),
            flight_id=flight.id,
            passenger_name=request.passenger_name,
            seat_no=request.seat_no,
            price=final_price,
            status="CONFIRMED",)
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Booking failed")
#        Simulated Payment API Endpoint
@app.post("/api/bookings/{pnr}/pay")
def simulate_payment(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.pnr == pnr).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    payment_success = random.choice([True, False])
    if payment_success:
        booking.status = "PAID"
        db.commit()
        return {"pnr": pnr, "status": "PAID"}
    booking.status = "PAYMENT_FAILED"
    db.commit()
    return {"pnr": pnr, "status": "PAYMENT_FAILED"}
#        Booking History Endpoint (All Bookings)
@app.get("/api/bookings", response_model=list[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
#        Get Booking By PNR
@app.get("/api/bookings/{pnr}", response_model=BookingResponse)
def get_booking_by_pnr(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.pnr == pnr).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
#        Booking Cancellation and Restore Seat Availability
@app.delete("/api/bookings/{pnr}")
def cancel_booking(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.pnr == pnr).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        return {"message": "Booking already cancelled"}
    flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
    flight.seats_available = min(flight.total_seats, flight.seats_available + 1)
    booking.status = "CANCELLED"
    db.commit()
    return {"pnr": pnr, "status": "CANCELLED"}            
#        Background Simulator to change demand/seats    
async def simulate_market_step():
    db = SessionLocal()
    try:
        flights = db.query(Flight).all()
        if not flights:
            return
        sample_size = min(5, len(flights))
        selected_flights = random.sample(flights, sample_size)
        for f in selected_flights:
            seat_change = random.randint(-5, 5)
            f.seats_available = max(0, min(f.total_seats, f.seats_available + seat_change))
            demand_value=None
            if hasattr(f, "demand_level"):
                demand_value=random.choice(["low", "medium", "high"])
                f.demand_level=demand_value
            final_price = calculate_dynamic_price(
                base_fare=float(f.base_fare),
                seats_available=f.seats_available,
                total_seats=f.total_seats,
                departure_time=f.departure_time,
                airline_name=f.airline_name,
                demand_level=demand_value,)
            history = FareHistory(
                flight_id=f.id,
                recorded_at=datetime.utcnow(),
                dynamic_price=final_price,
                seats_available=f.seats_available,
                demand_level=demand_value,
            )
            db.add(history)    
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[SIMULATOR ERROR] {e}")
    finally:
        db.close()
async def scheduler_loop(interval_seconds: int = 60):
#      Runs simulate_market_step() periodically.
    while True:
        await simulate_market_step()
        await asyncio.sleep(interval_seconds)
@app.on_event("startup")
async def start_background_simulator():
#      Start the demand/availability simulator when FastAPI starts.

    asyncio.create_task(scheduler_loop(60))    

