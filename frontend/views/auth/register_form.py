import streamlit as st

from core import session
from services import auth_service
from services.client import ApiError


def _account_fields():
    st.markdown("**Your account**")
    name = st.text_input("Your name")
    email = st.text_input("Email")
    phone = st.text_input("Phone (optional)")
    password = st.text_input(
        "Password", type="password", help="At least 6 characters"
    )
    return name, email, phone, password


def _hotel_fields() -> dict:
    st.markdown("**Your hotel**")
    return {
        "name": st.text_input("Hotel name"),
        "address": st.text_input("Address"),
        "city": st.text_input("City"),
        "coordinates": st.text_input(
            "Location",
            placeholder="19.0760, 72.8777",
            help="Right-click your hotel in Google Maps, click the numbers "
            "to copy them, and paste them here.",
        ),
    }


def render() -> None:
    kind = st.radio("I am a", ["Hotel", "Parking lot owner"], horizontal=True)

    with st.form(f"register_form_{kind}"):
        if kind == "Hotel":
            account_col, hotel_col = st.columns(2)
        else:
            account_col, hotel_col = st.container(), None

        with account_col:
            name, email, phone, password = _account_fields()

        hotel = None
        if hotel_col is not None:
            with hotel_col:
                hotel = _hotel_fields()

        submitted = st.form_submit_button(
            "Create account", type="primary", use_container_width=True
        )

    if not submitted:
        return

    required = [name, email, password] + (list(hotel.values()) if hotel else [])
    if not all(value.strip() for value in required):
        st.error("Please fill in all required fields.")
        return

    try:
        if hotel:
            auth_service.register_hotel(
                name.strip(),
                email.strip(),
                phone.strip() or None,
                password,
                {key: value.strip() for key, value in hotel.items()},
            )
        else:
            auth_service.register_owner(
                name.strip(), email.strip(), phone.strip() or None, password
            )
        session.log_in(email.strip(), password)
    except ApiError as error:
        st.error(error.message)
        return
    st.rerun()