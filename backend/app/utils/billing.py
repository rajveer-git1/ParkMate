import math
from datetime import datetime


def billable_hours(check_in: datetime, check_out: datetime) -> int:
    seconds = max((check_out - check_in).total_seconds(), 0)
    return max(math.ceil(seconds / 3600), 1)


def calculate_fee(
    check_in: datetime, check_out: datetime, price_per_hour: float
) -> float:
    return round(billable_hours(check_in, check_out) * price_per_hour, 2)