import streamlit as st  # type: ignore
from utils.db_utils import register_user

def show():
    st.subheader("Register")

    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")

    if st.button("Register", key="register_button"):
        if register_user(new_user, new_pass):
            st.success("Account successfully created! You can now log in.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("This username already exists.")
