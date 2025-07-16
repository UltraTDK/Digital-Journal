import streamlit as st # type: ignore
from utils.db_utils import create_user_table

# Importul paginilor principale
from pages import welcome_page, login_page, register_page, app_page

# Inițializare bază de date
create_user_table()

st.set_page_config(page_title="Digital Journal", layout="wide", initial_sidebar_state="collapsed")

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'username' not in st.session_state:
    st.session_state.username = None

# pagina Welcome definita ca pagina default
if 'page' not in st.session_state:
    st.session_state.page = "welcome"

# ------------------ User, Login, Registration ------------------ #
with st.container():
    col1, col2, col3= st.columns([3, 1, 1])
    with col1:
        if st.session_state.user_id:
            selected = st.selectbox(
                " ", [f"👤 {st.session_state.username}", "Disconnect"],
                label_visibility="collapsed",
                key="user_menu"
            )
            if selected == "Disconnect":
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.page = "welcome"
                st.success("You have successfully logged out.")
                st.rerun()
        else:
            st.markdown("👤 User")
    with col2:
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()
    with col3:
        if st.button("Registration"):
            st.session_state.page = "register"
            st.rerun()

# ------------------ Butonul de selectarea pagina ------------------ #
st.markdown("---")
col_nav, _ = st.columns([1.5, 8.5])
with col_nav:
    selected_page = st.selectbox(
        "Navigation:",
        options=["welcome", "login", "register", "app"],
        index=["welcome", "login", "register", "app"].index(st.session_state.page),
        key="page_selector"
    )
    # Verificare daca utilizatorul incearcă sa acceseze "app" fara sa fie logat
    if selected_page == "app" and st.session_state.user_id is None:
        st.warning("You must be logged in to access the app.")
        st.session_state.page = "login"
        st.rerun()
    
    elif selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

# ------------------ Navigare intre pagini ------------------ #
page = st.session_state.page

if page == "welcome":
    welcome_page.show()
elif page == "login":
    login_page.show()
elif page == "register":
    register_page.show()
elif page == "app":
    app_page.run_app_page()
