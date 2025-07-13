import random
from typing import Dict, Any
from datetime import datetime

 # Simulated hotel booking function for demo purposes.
 # NOTE: This is a placeholder; logic such as real-time availability, pricing, and validation is not implemented.
def book_hotel(
    location: str,
    check_in: str,
    check_out: str,
    guests: int = 1,
    room_type: str = "standard",
) -> Dict[str, Any]:
    """booking a hotel room."""
    hotels = {
        "Beijing": ["Beijing Grand Hotel", "Great Wall Inn", "Forbidden City Hotel"],
        "London": ["The Savoy", "The Ritz", "Park Plaza"],
        "New York": ["Plaza Hotel", "The Langham", "Times Square Inn"],
    }
    name = random.choice(hotels.get(location, [f"{location} International Hotel"]))
    nights = (datetime.strptime(check_out, "%Y-%m-%d") -
              datetime.strptime(check_in, "%Y-%m-%d")).days
    base = {"standard":100, "deluxe":180, "suite":300}.get(room_type, 120)
    total = base * nights * guests
    return {
        "confirmation_id": f"BK-{random.randint(100000,999999)}",
        "hotel": name,
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "room_type": room_type,
        "nights": nights,
        "total_price": total,
    }