import pandas as pd
import streamlit as st

from components import status
from components.formatting import money
from core import session
from services import lot_service
from services.client import ApiError

HOTEL_COLOR = "#2563EB"
AVAILABLE_COLOR = "#15803D"
FULL_COLOR = "#B91C1C"


def _map_points(hotel: dict, lots: list) -> pd.DataFrame:
    points = [
        {
            "latitude": hotel["latitude"],
            "longitude": hotel["longitude"],
            "color": HOTEL_COLOR,
            "size": 90,
        }
    ]
    for lot in lots:
        points.append(
            {
                "latitude": lot["latitude"],
                "longitude": lot["longitude"],
                "color": FULL_COLOR if lot["status"] == "Full" else AVAILABLE_COLOR,
                "size": 60,
            }
        )
    return pd.DataFrame(points)


def _row(lot: dict) -> dict:
    return {
        "Lot": lot["name"],
        "Distance": f"{lot['distance_km']} km",
        "Price": f"{money(lot['price_per_hour'])}/hr",
        "Free slots": f"{lot['available_slots']} of {lot['total_slots']}",
        "Status": status.lot_status(lot),
    }


def render() -> None:
    token = session.get_token()
    hotel = session.get_hotel()

    st.title(f"Lots near {hotel['name']}")
    st.caption("Nearest first, measured in a straight line")

    radius_col, filter_col = st.columns(2)
    radius = radius_col.slider("Search radius (km)", 1, 50, 10)
    only_available = filter_col.checkbox("Only show lots with free slots")

    try:
        lots = lot_service.nearby_lots(token, radius, only_available)
    except ApiError as error:
        session.show_error(error)
        return

    if lots:
        st.dataframe([_row(lot) for lot in lots], hide_index=True)
    else:
        st.info(f"No lots within {radius} km. Try a bigger radius.")

    st.markdown("**Map**")
    st.map(
        _map_points(hotel, lots),
        latitude="latitude",
        longitude="longitude",
        color="color",
        size="size",
    )
    st.caption("Blue: your hotel. Green: lots with space. Red: full lots.")