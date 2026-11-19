import streamlit as st


def push(kind: str, text: str) -> None:
    st.session_state["flash"] = (kind, text)


def show() -> None:
    message = st.session_state.pop("flash", None)
    if not message:
        return
    kind, text = message
    {"success": st.success, "error": st.error, "info": st.info}[kind](text)