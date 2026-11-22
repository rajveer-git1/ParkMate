import logging

import streamlit as st

import navigation
from components import sidebar
from core import session
from views.auth import auth_page

logger = logging.getLogger("parkmate")

st.set_page_config(page_title="ParkMate", page_icon="🅿️", layout="wide")


def run_screen(screen) -> None:
    try:
        screen()
    except Exception as error:
        logger.exception("A screen crashed")
        st.error(
            "Something went wrong on this screen. Please try again, "
            "or log out and back in."
        )
        with st.expander("Technical details"):
            st.code(f"{type(error).__name__}: {error}")


def main() -> None:
    if not session.is_logged_in():
        run_screen(auth_page.render)
        return

    menu = navigation.menu_for(session.get_role())
    choice = sidebar.render(menu)
    run_screen(menu[choice])


main()