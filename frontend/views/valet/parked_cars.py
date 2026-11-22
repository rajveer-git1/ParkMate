import streamlit as st

from components import booking_rows, checkout, pager
from components.formatting import car_details, when
from core import session
from services import booking_service
from services.client import ApiError

PREFIX = "valet_parked"

COLUMNS = [
    ("Car", 1.6, lambda b: b["vehicle_number"]),
    ("Guest", 1.7, lambda b: b["guest_name"]),
    ("Lot", 1.5, lambda b: b["lot_name"]),
    ("Since", 1.5, lambda b: when(b["check_in_time"])),
    ("Details", 2.0, car_details),
]


def render() -> None:
    token = session.get_token()
    hotel = session.get_hotel()

    st.title("Cars parked now")
    st.caption(f"Cars at {hotel['name']} that have not been returned")
    checkout.show_receipt()

    search = st.text_input(
        "Search",
        placeholder="Car number or guest",
        key=f"{PREFIX}_search",
        on_change=pager.reset,
        args=(PREFIX,),
    )
    page = pager.current_page(PREFIX)

    try:
        rows = booking_service.list_bookings(
            token,
            search=search.strip() or None,
            limit=pager.PAGE_SIZE + 1,
            offset=page * pager.PAGE_SIZE,
        )
    except ApiError as error:
        session.show_error(error)
        return

    has_next = len(rows) > pager.PAGE_SIZE
    rows = rows[: pager.PAGE_SIZE]

    if not rows:
        message = (
            "No parked cars match your search."
            if search.strip()
            else "No cars are parked right now."
        )
        st.info(message)
    else:
        booking_rows.render(rows, COLUMNS, token=token, key_prefix=PREFIX)

    pager.render(PREFIX, has_next)