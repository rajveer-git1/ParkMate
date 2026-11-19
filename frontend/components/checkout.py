import streamlit as st

from components.formatting import money, parked_for, when
from core import session
from services import booking_service
from services.client import ApiError


def return_car(token: str, booking: dict) -> None:
    try:
        result = booking_service.checkout(token, booking["id"])
    except ApiError as error:
        session.show_error(error)
        return
    st.session_state["receipt"] = result
    st.rerun()


def show_receipt() -> None:
    booking = st.session_state.pop("receipt", None)
    if not booking:
        return

    hours = max(round(booking["total_fee"] / booking["price_per_hour"]), 1)
    unit = "hour" if hours == 1 else "hours"

    with st.container(border=True):
        st.success(f"Car returned: {booking['vehicle_number']}")
        details, fee = st.columns([3, 1])
        details.write(f"**Checked in:** {when(booking['check_in_time'])}")
        details.write(f"**Returned:** {when(booking['check_out_time'])}")
        details.write(
            f"**Time parked:** "
            f"{parked_for(booking['check_in_time'], booking['check_out_time'])} "
            f"(billed as {hours} {unit})"
        )
        details.write(f"**Rate:** {money(booking['price_per_hour'])} per hour")
        fee.metric("Total fee", money(booking["total_fee"]))