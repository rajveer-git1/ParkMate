import streamlit as st

from core import session
from core.config import ROLE_LABELS


def render(menu: dict) -> str:
    user = session.get_user()
    st.sidebar.markdown("### 🅿️ ParkMate")
    st.sidebar.markdown(f"**{user['name']}**  \n{ROLE_LABELS[user['role']]}")
    st.sidebar.divider()
    choice = st.sidebar.radio("Menu", list(menu), label_visibility="collapsed")
    st.sidebar.divider()
    if st.sidebar.button("Log out", use_container_width=True):
        session.logout()
        st.rerun()
    return choice