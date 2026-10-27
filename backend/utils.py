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