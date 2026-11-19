import streamlit as st

from components import booking_rows, checkout, pager, status
from components.formatting import money, when
from core import session
from services import booking_service
from services.client import ApiError

PREFIX = "hotel_bookings"

COLUMNS = [
    ("Car", 1.6, lambda b: b["vehicle_number"]),
    ("Guest", 1.7, lambda b: b["guest_name"]),
    ("Lot", 1.5, lambda b: b["lot_name"]),
    ("Valet", 1.2, lambda b: b["valet_name"]),
    ("Checked in", 1.5, lambda b: when(b["check_in_time"])),
    ("Fee", 1.0, lambda b: money(b["total_fee"])),
    ("Status", 1.5, lambda b: status.booking_status(b["status"])),
]


def render() -> None:
    token = session.get_token()
    hotel = session.get_hotel()

    st.title(f"Bookings at {hotel['name']}")
    st.caption("Every car your valets have parked")
    checkout.show_receipt()

    metrics_box = st.container()

    status_col, search_col = st.columns(2)
    status_choice = status_col.selectbox(
        "Status",
        status.FILTER_CHOICES,
        key=f"{PREFIX}_status",
        on_change=pager.reset,
        args=(PREFIX,),
    )
    search = search_col.text_input(
        "Search",
        placeholder="Car number or guest",
        key=f"{PREFIX}_search",
        on_change=pager.reset,
        args=(PREFIX,),
    )

    page = pager.current_page(PREFIX)

    try:
        summary = booking_service.summary(token)
        rows = booking_service.list_bookings(
            token,
            status=status.filter_value(status_choice),
            search=search.strip() or None,
            limit=pager.PAGE_SIZE + 1,
            offset=page * pager.PAGE_SIZE,
        )
    except ApiError as error:
        session.show_error(error)
        return

    with metrics_box:
        total_col, parked_col, done_col, spend_col = st.columns(4)
        total_col.metric("Total bookings", summary["total_bookings"])
        parked_col.metric("Parked now", summary["parked_now"])
        done_col.metric("Completed", summary["completed"])
        spend_col.metric("Parking spend", money(summary["total_fees"]))

    has_next = len(rows) > pager.PAGE_SIZE
    rows = rows[: pager.PAGE_SIZE]

    if not rows:
        st.info("No bookings match these filters.")
    else:
        booking_rows.render(rows, COLUMNS, token=token, key_prefix=PREFIX)

    pager.render(PREFIX, has_next)