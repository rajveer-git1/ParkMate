import streamlit as st

from core import session
from services.client import ApiError


def render() -> None:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(
            "Log in", type="primary", use_container_width=True
        )

    if not submitted:
        return
    if not email.strip() or not password:
        st.error("Please enter your email and password.")
        return

    try:
        session.log_in(email.strip(), password)
    except ApiError as error:
        st.error(error.message)
        return
    st.rerun()