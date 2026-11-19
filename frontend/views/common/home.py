import streamlit as st

from core import session
from core.config import ROLE_LABELS


def render() -> None:
    user = session.get_user()
    st.title(f"Welcome, {user['name']}")
    st.write(
        f"You are logged in as **{ROLE_LABELS[user['role']]}** ({user['email']})."
    )
    st.info(
        "Your screens will appear in the menu on the left as we build them "
        "over the next few days."
    )