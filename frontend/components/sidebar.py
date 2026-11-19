import streamlit as st

from core import session
from core.config import ROLE_LABELS


def render(menu: dict) -> str:
    user = session.get_user()
    hotel = session.get_hotel()

    if st.session_state.get("menu_choice") not in menu:
        st.session_state["menu_choice"] = next(iter(menu))

    st.sidebar.markdown("### 🅿️ ParkMate")
    st.sidebar.markdown(f"**{user['name']}**  \n{ROLE_LABELS[user['role']]}")
    if hotel:
        st.sidebar.caption(hotel["name"])
    st.sidebar.divider()
    choice = st.sidebar.radio(
        "Menu", list(menu), key="menu_choice", label_visibility="collapsed"
    )
    st.sidebar.divider()
    if st.sidebar.button("Log out"):
        session.logout()
        st.rerun()
    return choice