"""Reference data for transport feasibility.

A curated (non-exhaustive) set of cities with commercial airports, plus
nearest-airport hints for a few common non-airport towns, and booking-app
suggestions per mode. This is intentionally simple, file-based data — for full
accuracy a real geocoding/airport API would replace `has_airport` /
`nearest_airport`.
"""

from __future__ import annotations

# Cities with a commercial airport (lowercased). Non-exhaustive.
AIRPORT_CITIES: set[str] = {
    # India — metros & major
    "hyderabad", "mumbai", "delhi", "new delhi", "bengaluru", "bangalore",
    "chennai", "kolkata", "pune", "ahmedabad", "goa", "kochi", "cochin",
    "jaipur", "lucknow", "visakhapatnam", "vizag", "vijayawada", "rajahmundry",
    "tirupati", "coimbatore", "thiruvananthapuram", "trivandrum", "guwahati",
    "bhubaneswar", "indore", "nagpur", "varanasi", "amritsar", "srinagar",
    "leh", "udaipur", "jodhpur", "patna", "ranchi", "raipur", "dehradun",
    "mangalore", "madurai", "bagdogra", "port blair", "surat",
    # international
    "tokyo", "osaka", "paris", "london", "new york", "dubai", "singapore",
    "bangkok", "denpasar", "bali", "zurich", "geneva", "rome", "barcelona",
    "frankfurt", "sydney", "kuala lumpur",
}

# Nearest major airport hint for some common airport-less towns (lowercased).
NEAREST_AIRPORT: dict[str, str] = {
    "malikipuram": "Rajahmundry (RJA), ~70 km",
    "narasapur": "Rajahmundry (RJA), ~55 km",
    "naraspur": "Rajahmundry (RJA), ~55 km",
    "amalapuram": "Rajahmundry (RJA), ~50 km",
    "bhimavaram": "Vijayawada (VGA) / Rajahmundry (RJA)",
    "palakollu": "Rajahmundry (RJA), ~60 km",
}

BOOKING_APPS: dict[str, list[str]] = {
    "flight": ["Google Flights", "Skyscanner", "MakeMyTrip", "Cleartrip"],
    "train": ["IRCTC Rail Connect", "ConfirmTkt", "RailYatri"],
    "bus": ["RedBus", "AbhiBus", "MakeMyTrip Bus"],
}


def _norm(city: str | None) -> str:
    return (city or "").strip().lower()


def has_airport(city: str | None) -> bool:
    """True if the (possibly messy) city string references an airport city."""
    c = _norm(city)
    return bool(c) and any(a in c for a in AIRPORT_CITIES)


def nearest_airport(city: str | None) -> str | None:
    """Return a nearest-airport hint for a known airport-less town, else None."""
    c = _norm(city)
    for town, airport in NEAREST_AIRPORT.items():
        if town in c:
            return airport
    return None
