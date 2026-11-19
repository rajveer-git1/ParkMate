import streamlit as st

PAGE_SIZE = 20


def _key(prefix: str) -> str:
    return f"{prefix}_page"


def current_page(prefix: str) -> int:
    return st.session_state.setdefault(_key(prefix), 0)


def reset(prefix: str) -> None:
    st.session_state[_key(prefix)] = 0


def _change(prefix: str, step: int) -> None:
    st.session_state[_key(prefix)] += step


def render(prefix: str, has_next: bool) -> None:
    page = current_page(prefix)
    prev_col, page_col, next_col = st.columns([1, 3, 1])
    prev_col.button(
        "Previous",
        key=f"{prefix}_prev",
        disabled=page == 0,
        on_click=_change,
        args=(prefix, -1),
    )
    page_col.caption(f"Page {page + 1}")
    next_col.button(
        "Next",
        key=f"{prefix}_next",
        disabled=not has_next,
        on_click=_change,
        args=(prefix, 1),
    )