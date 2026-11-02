import math


def parse_coordinates(text: str) -> tuple[float, float]:
    cleaned = text.strip().strip("()")
    parts = cleaned.split(",")

    if len(parts) != 2:
        raise ValueError("Coordinates must look like: 19.0760, 72.8777")

    try:
        latitude = float(parts[0].strip())
        longitude = float(parts[1].strip())
    except ValueError:
        raise ValueError("Coordinates must be numbers, like: 19.0760, 72.8777")

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    return latitude, longitude


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return earth_radius_km * 2 * math.asin(math.sqrt(a))