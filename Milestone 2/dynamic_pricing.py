from datetime import datetime
from typing import Literal,Optional
import random
DemandLevel = Literal["low", "medium", "high"]
def _seat_factor(seats_available: int, total_seats: int) -> float:
    """
    Compute price adjustment based on remaining seats.
    Returns a factor like -0.10 (10% cheaper) or +0.25 (25% more).
    """
    if total_seats <= 0:
        return 0.0
    ratio = seats_available / total_seats
    if ratio >= 0.7:
        # Lots of seats left -> small discount
        return -0.10
    elif 0.4 <= ratio < 0.7:
        # Normal range -> no change
        return 0.0
    else:
        # Very few seats left -> price up
        return +0.25
def _time_factor(departure_time) -> float:
    """
    Compute price adjustment based on how close the departure is.
    """
    now = datetime.now()
    diff = departure_time - now
    hours_to_departure = diff.total_seconds() / 3600
    if hours_to_departure <= 0:
        # Flight already departed or in progress
        return 0.0
    elif hours_to_departure <= 24:
        # Very last minute -> big increase
        return +0.40
    elif hours_to_departure <= 72:
        # 1–3 days -> moderate increase
        return +0.20
    elif hours_to_departure <= 168:
        # 3–7 days -> small increase
        return +0.10
    else:
        # More than a week -> no urgency
        return 0.0
def _demand_factor(demand_level: Optional[DemandLevel]) -> float:
    """
    Price adjustment based on demand.
    If demand_level is None, simulate it randomly.
    """
    if demand_level is None:
        demand_level = random.choice(["low", "medium", "high"])
    if demand_level == "low":
        return -0.05
    elif demand_level == "medium":
        return 0.0
    else:
        return +0.20
def _tier_factor(airline_name: str) -> float:
    """
    Simple tier system based on airline name.
    Premium airlines: slight increase
    Budget airlines: slight discount
    Others: no change
    """
    premium_airlines = {"AirIndia", "Vistara", "Emirates"}
    budget_airlines = {"IndiGo", "SpiceJet", "AirAsia"}
    if airline_name in premium_airlines:
        return +0.10
    elif airline_name in budget_airlines:
        return -0.05
    else:
        return 0.0
def calculate_dynamic_price(
    base_fare: float,
    seats_available: int,
    total_seats: int,
    departure_time,
    airline_name: str,
    demand_level: Optional[DemandLevel] = None,
) -> float:
    """
    Main pricing function used by FastAPI.
    Returns the final dynamic price as a float.
    """
    if base_fare <= 0:
        return float(base_fare)
    seat_adj = _seat_factor(seats_available, total_seats)
    time_adj = _time_factor(departure_time)
    demand_adj = _demand_factor(demand_level)
    tier_adj = _tier_factor(airline_name)
    total_factor = 1.0 + seat_adj + time_adj + demand_adj + tier_adj
    # clamp between 60% and 220% of base_fare. dynamic price ranges from 0.6*base_fare to 2.2*base_fare
    total_factor = max(0.6, min(total_factor, 2.2))
    dynamic_price = round(base_fare * total_factor, 2)
    return float(dynamic_price)