from datetime import datetime
from typing import Optional


def money(value: Optional[float]) -> str:
    if value is None:
        return "-"
    text = f"{value:,.2f}"
    if text.endswith(".00"):
        text = text[:-3]
    return f"Rs {text}"


def when(value: Optional[str]) -> str:
    if not value:
        return "-"
    return datetime.fromisoformat(value).strftime("%d %b, %H:%M")


def parked_for(check_in: str, check_out: str) -> str:
    seconds = (
        datetime.fromisoformat(check_out) - datetime.fromisoformat(check_in)
    ).total_seconds()
    hours, minutes = divmod(max(int(seconds // 60), 0), 60)
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"