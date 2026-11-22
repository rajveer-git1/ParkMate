import streamlit as st

from components import pager, status
from components.formatting import car_details, money, when
from core import session
from services import booking_service, lot_service
from services.client import ApiError

PREFIX = "owner_bookings"


def _row(booking: dict) -> dict:
    
    return {
        "Car": booking["vehicle_number"],
        "Details": car_details(booking),
        "Guest": booking["guest_name"],
        "Hotel": booking["hotel_name"],
        "Lot": booking["lot_name"],
        "Checked in": when(booking["check_in_time"]),
        "Fee": money(booking["total_fee"]),
        "Status": status.booking_status(booking["status"]),
    }


def render() -> None:
    token = session.get_token()

    st.title("Bookings in my lots")
    st.caption("Cars from every hotel that use your lots")

    try:
        lots = lot_service.my_lots(token)
    except ApiError as error:
        session.show_error(error)
        return
    lot_names = {lot["id"]: lot["name"] for lot in lots}

    metrics_box = st.container()

    status_col, lot_col, search_col = st.columns(3)
    status_choice = status_col.selectbox(
        "Status",
        status.FILTER_CHOICES,
        key=f"{PREFIX}_status",
        on_change=pager.reset,
        args=(PREFIX,),
    )
    lot_choice = lot_col.selectbox(
        "Lot",
        [None] + list(lot_names),
        format_func=lambda lot_id: "All lots" if lot_id is None else lot_names[lot_id],
        key=f"{PREFIX}_lot",
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
        summary = booking_service.summary(token, lot_choice)
        rows = booking_service.list_bookings(
            token,
            status=status.filter_value(status_choice),
            lot_id=lot_choice,
            search=search.strip() or None,
            limit=pager.PAGE_SIZE + 1,
            offset=page * pager.PAGE_SIZE,
        )
    except ApiError as error:
        session.show_error(error)
        return

    with metrics_box:
        total_col, parked_col, done_col, fees_col = st.columns(4)
        total_col.metric("Total bookings", summary["total_bookings"])
        parked_col.metric("Parked now", summary["parked_now"])
        done_col.metric("Completed", summary["completed"])
        fees_col.metric("Total fees", money(summary["total_fees"]))

    has_next = len(rows) > pager.PAGE_SIZE
    rows = rows[: pager.PAGE_SIZE]

    if not rows:
        st.info("No bookings match these filters.")
    else:
        st.dataframe([_row(booking) for booking in rows], hide_index=True)

    pager.render(PREFIX, has_next)