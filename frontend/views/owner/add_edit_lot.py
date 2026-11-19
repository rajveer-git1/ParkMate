import streamlit as st

from components import flash
from core import session
from services import lot_service
from services.client import ApiError

ADD_MODE = "Add new lot"
EDIT_MODE = "Edit existing lot"

LOCATION_HELP = (
    "Right-click the place in Google Maps, click the numbers to copy them, "
    "and paste them here."
)


def _same_location(text: str, lot: dict) -> bool:
    try:
        latitude, longitude = (
            float(part) for part in text.replace("(", "").replace(")", "").split(",")
        )
    except ValueError:
        return False
    return latitude == lot["latitude"] and longitude == lot["longitude"]


def _add_form() -> None:
    version = st.session_state.get("add_lot_version", 0)

    with st.form(f"add_lot_form_{version}"):
        name = st.text_input("Lot name")
        address = st.text_input("Address")
        city_col, location_col = st.columns(2)
        city = city_col.text_input("City")
        coordinates = location_col.text_input(
            "Location", placeholder="19.0760, 72.8777", help=LOCATION_HELP
        )
        slots_col, price_col = st.columns(2)
        total_slots = slots_col.number_input(
            "Total slots", min_value=1, value=10, step=1
        )
        price = price_col.number_input(
            "Price per hour (Rs)", min_value=1.0, value=50.0, step=5.0, format="%.2f"
        )
        submitted = st.form_submit_button("Save lot", type="primary")

    if not submitted:
        return
    if not all(value.strip() for value in (name, address, city, coordinates)):
        st.error("Please fill in all the fields.")
        return

    payload = {
        "name": name.strip(),
        "address": address.strip(),
        "city": city.strip(),
        "coordinates": coordinates.strip(),
        "total_slots": int(total_slots),
        "price_per_hour": float(price),
    }
    try:
        lot = lot_service.create_lot(session.get_token(), payload)
    except ApiError as error:
        session.show_error(error)
        return

    st.session_state["add_lot_version"] = version + 1
    flash.push("success", f"Lot '{lot['name']}' added. It now appears under My Lots.")
    st.rerun()


def _edit_form() -> None:
    token = session.get_token()
    try:
        lots = lot_service.my_lots(token)
    except ApiError as error:
        session.show_error(error)
        return

    if not lots:
        st.info("You have no lots yet. Use 'Add new lot' first.")
        return

    by_id = {lot["id"]: lot for lot in lots}
    ids = list(by_id)
    preselected = st.session_state.pop("edit_lot_id", None)
    index = ids.index(preselected) if preselected in by_id else 0

    lot_id = st.selectbox(
        "Choose a lot",
        ids,
        index=index,
        format_func=lambda lot_id: by_id[lot_id]["name"],
        key="edit_lot_choice",
    )
    lot = by_id[lot_id]

    with st.form(f"edit_lot_form_{lot_id}"):
        name = st.text_input("Lot name", value=lot["name"], key=f"edit_name_{lot_id}")
        address = st.text_input(
            "Address", value=lot["address"], key=f"edit_address_{lot_id}"
        )
        city_col, location_col = st.columns(2)
        city = city_col.text_input("City", value=lot["city"], key=f"edit_city_{lot_id}")
        coordinates = location_col.text_input(
            "Location",
            value=f"{lot['latitude']}, {lot['longitude']}",
            help=LOCATION_HELP,
            key=f"edit_location_{lot_id}",
        )
        slots_col, price_col = st.columns(2)
        total_slots = slots_col.number_input(
            "Total slots",
            min_value=1,
            value=int(lot["total_slots"]),
            step=1,
            key=f"edit_slots_{lot_id}",
        )
        price = price_col.number_input(
            "Price per hour (Rs)",
            min_value=1.0,
            value=float(lot["price_per_hour"]),
            step=5.0,
            format="%.2f",
            key=f"edit_price_{lot_id}",
        )
        is_active = st.checkbox(
            "Lot is active",
            value=lot["is_active"],
            help="Inactive lots are hidden from hotels and valets.",
            key=f"edit_active_{lot_id}",
        )
        submitted = st.form_submit_button("Save changes", type="primary")

    if not submitted:
        return
    if not all(value.strip() for value in (name, address, city, coordinates)):
        st.error("Please fill in all the fields.")
        return

    entered = {
        "name": name.strip(),
        "address": address.strip(),
        "city": city.strip(),
        "total_slots": int(total_slots),
        "price_per_hour": float(price),
        "is_active": is_active,
    }
    changes = {key: value for key, value in entered.items() if value != lot[key]}
    if not _same_location(coordinates.strip(), lot):
        changes["coordinates"] = coordinates.strip()

    if not changes:
        st.info("Nothing to change.")
        return

    try:
        updated = lot_service.update_lot(token, lot_id, changes)
    except ApiError as error:
        session.show_error(error)
        return

    flash.push("success", f"Lot '{updated['name']}' updated.")
    st.rerun()


def render() -> None:
    st.title("Add or edit a lot")
    flash.show()

    mode = st.radio(
        "What do you want to do?",
        [ADD_MODE, EDIT_MODE],
        key="lot_form_mode",
        horizontal=True,
        label_visibility="collapsed",
    )
    if mode == ADD_MODE:
        _add_form()
    else:
        _edit_form()