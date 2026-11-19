from typing import Optional

LOT_DOTS = {"Available": "🟢", "Full": "🔴", "Inactive": "⚫"}
BOOKING_DOTS = {"parked": "🟡", "completed": "⚪"}
FILTER_CHOICES = ["All", "Parked", "Completed"]


def lot_status(lot: dict) -> str:
    state = "Inactive" if not lot["is_active"] else lot["status"]
    return f"{LOT_DOTS[state]} {state}"


def booking_status(state: str) -> str:
    return f"{BOOKING_DOTS[state]} {state.capitalize()}"


def filter_value(choice: str) -> Optional[str]:
    return None if choice == "All" else choice.lower()