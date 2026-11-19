import streamlit as st

from services import auth_service, hotel_service
from services.client import ApiError


def is_logged_in() -> bool:
    return "token" in st.session_state


def log_in(email: str, password: str) -> None:
    token_data = auth_service.login(email, password)
    token = token_data["access_token"]
    user = auth_service.get_me(token)
    hotel = None
    if user["role"] in ("hotel", "valet"):
        hotel = hotel_service.my_hotel(token)

    st.session_state["token"] = token
    st.session_state["role"] = token_data["role"]
    st.session_state["user"] = user
    st.session_state["hotel"] = hotel


def get_token():
    return st.session_state.get("token")


def get_role():
    return st.session_state.get("role")


def get_user():
    return st.session_state.get("user")


def get_hotel():
    return st.session_state.get("hotel")


def logout() -> None:
    st.session_state.clear()


def show_error(error: ApiError) -> None:
    if error.status_code == 401:
        st.session_state.clear()
        st.session_state["notice"] = "Your session expired. Please log in again."
        st.rerun()
    st.error(error.message)