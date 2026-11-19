from services.client import request


def my_lots(token: str) -> list:
    return request("GET", "/lots/mine", token=token)


def create_lot(token: str, payload: dict) -> dict:
    return request("POST", "/lots", token=token, json=payload)


def update_lot(token: str, lot_id: int, changes: dict) -> dict:
    return request("PUT", f"/lots/{lot_id}", token=token, json=changes)


def nearby_lots(token: str, radius_km: float, only_available: bool) -> list:
    params = {"radius_km": radius_km, "only_available": str(only_available).lower()}
    return request("GET", "/lots/nearby", token=token, params=params)