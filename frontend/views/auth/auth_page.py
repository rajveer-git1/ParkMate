import streamlit as st

from views.auth import login_form, register_form


def render() -> None:
    _, middle, _ = st.columns([1, 3, 1])
    with middle:
        st.markdown("# 🅿️ ParkMate")
        st.caption("Hotel valet and parking lot management")

        notice = st.session_state.pop("notice", None)
        if notice:
            st.warning(notice)

        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            login_form.render()
        with register_tab:
            register_form.render()