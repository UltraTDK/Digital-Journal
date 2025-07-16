import streamlit as st  # type: ignore
from utils.db_utils import login_user

def show():
    st.subheader("Login")
    
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login",  key="login_button"):
        user_id = login_user(user, password)
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.username = user
            st.success("Login successful! Redirecting...")
            st.session_state.page = "app"
            st.rerun()
        else:
            st.error("Incorrect credentials.")