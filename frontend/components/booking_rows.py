import streamlit as st

from components import checkout


def render(bookings: list, columns: list, *, token: str, key_prefix: str) -> None:
    widths = [width for _, width, _ in columns] + [1.1]

    header = st.columns(widths)
    for slot, (title, _, _) in zip(header, columns):
        slot.caption(title)
    header[-1].caption("Action")

    for booking in bookings:
        row = st.columns(widths)
        for slot, (_, _, getter) in zip(row, columns):
            slot.write(getter(booking))
        if booking["status"] == "parked":
            pressed = row[-1].button(
                "Return", key=f"{key_prefix}_return_{booking['id']}"
            )
            if pressed:
                checkout.return_car(token, booking)