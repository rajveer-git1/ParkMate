import streamlit as st

from components import flash
from components.formatting import money
from core import session
from services import booking_service, lot_service
from services.client import ApiError

SEARCH_RADIUS_KM = 50
CAR_NUMBER_HELP = (
    "Spaces and dashes are ignored. MH 01 AB 1234 and MH-01-AB-1234 "
    "are the same car."
)


def _lot_label(lot: dict) -> str:
    return (
        f"{lot['name']}  -  {lot['distance_km']} km  -  "
        f"{lot['available_slots']} free  -  {money(lot['price_per_hour'])}/hr"
    )


def render() -> None:
    token = session.get_token()
    hotel = session.get_hotel()

    st.title("Check in a car")
    st.caption(f"Park a guest's car for {hotel['name']} in a lot that has space")
    flash.show()

    try:
        lots = lot_service.nearby_lots(token, SEARCH_RADIUS_KM, only_available=True)
    except ApiError as error:
        session.show_error(error)
        return

    if not lots:
        st.warning(
            f"No lots with free space within {SEARCH_RADIUS_KM} km. "
            "Please ask your hotel manager."
        )
        return

    by_id = {lot["id"]: lot for lot in lots}
    version = st.session_state.get("check_in_version", 0)

    with st.form(f"check_in_form_{version}"):
        lot_id = st.selectbox(
            "Parking lot",
            list(by_id),
            format_func=lambda lot_id: _lot_label(by_id[lot_id]),
        )
        guest_col, phone_col = st.columns(2)
        guest_name = guest_col.text_input("Guest name")
        guest_phone = phone_col.text_input("Guest phone")
        vehicle_number = st.text_input(
            "Car number", placeholder="MH 01 AB 1234", help=CAR_NUMBER_HELP
        )
        model_col, color_col = st.columns(2)
        vehicle_model = model_col.text_input("Car model (optional)")
        vehicle_color = color_col.text_input("Car color (optional)")
        submitted = st.form_submit_button("Check in car", type="primary")

    if not submitted:
        return
    if not all(
        value.strip() for value in (guest_name, guest_phone, vehicle_number)
    ):
        st.error("Please fill in the guest name, guest phone and car number.")
        return

    payload = {
        "lot_id": lot_id,
        "guest_name": guest_name.strip(),
        "guest_phone": guest_phone.strip(),
        "vehicle_number": vehicle_number.strip(),
        "vehicle_model": vehicle_model.strip() or None,
        "vehicle_color": vehicle_color.strip() or None,
    }
    try:
        booking = booking_service.check_in(token, payload)
    except ApiError as error:
        session.show_error(error)
        return

    st.session_state["check_in_version"] = version + 1
    flash.push(
        "success",
        f"Car {booking['vehicle_number']} is parked at "
        f"{by_id[lot_id]['name']} (booking {booking['id']}).",
    )
    st.rerun()