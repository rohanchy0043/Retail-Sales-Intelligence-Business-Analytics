import streamlit as st


def metric(label: str, value: str, help_text: str | None = None, delta: str | None = None) -> None:
    st.metric(label, value, delta=delta, help=help_text)


def filter_reset_button() -> None:
    if st.button("Reset Filters", width="stretch"):
        for key in list(st.session_state):
            if key.endswith("_filter"):
                del st.session_state[key]
        st.rerun()
