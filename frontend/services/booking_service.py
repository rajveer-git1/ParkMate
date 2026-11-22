from typing import Optional

from services.client import request


def list_bookings(
    token: str,
    *,
    status: Optional[str] = None,
    lot_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list:
    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
    if lot_id is not None:
        params["lot_id"] = lot_id
    if search:
        params["search"] = search
    return request("GET", "/bookings", token=token, params=params)


def summary(token: str, lot_id: Optional[int] = None) -> dict:
    params = {"lot_id": lot_id} if lot_id is not None else None
    return request("GET", "/bookings/summary", token=token, params=params)


def checkout(token: str, booking_id: int) -> dict:
    return request("POST", f"/bookings/{booking_id}/checkout", token=token)


def check_in(token: str, payload: dict) -> dict:
    return request("POST", "/bookings", token=token, json=payload)