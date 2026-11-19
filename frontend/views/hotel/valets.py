import streamlit as st

from components import flash
from core import session
from services import user_service
from services.client import ApiError


def render() -> None:
    hotel = session.get_hotel()

    st.title("Valets")
    st.caption(f"New valets join {hotel['name']} automatically")
    flash.show()

    version = st.session_state.get("valet_form_version", 0)

    with st.form(f"valet_form_{version}"):
        name = st.text_input("Valet name")
        email = st.text_input("Email")
        phone = st.text_input("Phone (optional)")
        password = st.text_input(
            "Password", type="password", help="At least 6 characters"
        )
        submitted = st.form_submit_button("Create valet account", type="primary")

    if not submitted:
        return
    if not all(value.strip() for value in (name, email, password)):
        st.error("Please fill in the name, email and password.")
        return

    payload = {
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip() or None,
        "password": password,
    }
    try:
        valet = user_service.create_valet(session.get_token(), payload)
    except ApiError as error:
        session.show_error(error)
        return

    st.session_state["valet_form_version"] = version + 1
    flash.push(
        "success", f"Valet account created for {valet['name']} ({valet['email']})."
    )
    st.rerun()