import streamlit as st

import navigation
from components import sidebar
from core import session
from views.auth import auth_page

st.set_page_config(page_title="ParkMate", page_icon="🅿️", layout="wide")


def main() -> None:
    if not session.is_logged_in():
        auth_page.render()
        return

    menu = navigation.menu_for(session.get_role())
    choice = sidebar.render(menu)
    menu[choice]()


main()