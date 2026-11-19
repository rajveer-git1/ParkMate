import streamlit as st

from components import flash, status
from components.formatting import money
from core import session
from core.config import MENU_ADD_EDIT_LOT
from services import booking_service, lot_service
from services.client import ApiError


def _open_editor(lot_id: int) -> None:
    st.session_state["edit_lot_id"] = lot_id
    st.session_state["lot_form_mode"] = "Edit existing lot"
    st.session_state["menu_choice"] = MENU_ADD_EDIT_LOT


def _lot_card(lot: dict) -> None:
    with st.container(border=True):
        info, usage, state, action = st.columns([3, 3, 2, 1])

        info.markdown(f"**{lot['name']}**")
        info.caption(f"{lot['address']}, {lot['city']}")
        info.write(f"{money(lot['price_per_hour'])} per hour")

        used = lot["occupied_slots"]
        total = lot["total_slots"]
        usage.progress(min(used / total, 1.0), text=f"{used} of {total} slots used")

        state.write(status.lot_status(lot))

        action.button(
            "Edit", key=f"edit_{lot['id']}", on_click=_open_editor, args=(lot["id"],)
        )


def render() -> None:
    token = session.get_token()

    st.title("My parking lots")
    st.caption("Everything you own, with live Full / Available status")
    flash.show()

    try:
        lots = lot_service.my_lots(token)
        summary = booking_service.summary(token)
    except ApiError as error:
        session.show_error(error)
        return

    lots_col, parked_col, fees_col = st.columns(3)
    lots_col.metric("Lots", len(lots))
    parked_col.metric("Cars parked now", summary["parked_now"])
    fees_col.metric("Fees earned", money(summary["total_fees"]))

    if not lots:
        st.info("You have no lots yet. Open 'Add / Edit Lot' to add your first one.")
        return

    for lot in lots:
        _lot_card(lot)

    st.info("A lot shows Full when parked cars reach its total slots.")