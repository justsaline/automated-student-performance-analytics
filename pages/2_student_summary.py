import streamlit as st

if not st.session_state.get("data_ready", False):
    st.warning("Please upload and process data on the main page first.")
    st.stop()