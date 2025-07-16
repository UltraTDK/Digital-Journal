import streamlit as st # type: ignore
import pandas as pd # type: ignore

from utils.system_status import check_system_status
from utils.app_sections import _text_analysis, _image_analysis, _journal_page, _emotional_report

def run_app_page():
    st.header(f"👤 Welcome, {st.session_state.username}")

    # Verificare sistem pentru a ne asigura ca totul functioneaza cum trebuie
    with st.expander("🔍 System check (click for details)", expanded=False):
        system = check_system_status()
        for modul, ok in system.items():
            if ok:
                st.success(f"{modul} — OK")
            else:
                st.error(f"{modul} — Error")

    # Selectarea modului dorit
    app_mode = st.selectbox("Select the mode:", [
        "Text analysis", 
        "Image analysis", 
        "Journal Page", 
        "Emotional Reports"
    ])    

    if app_mode == "Text analysis":
        _text_analysis()

    elif app_mode == "Image analysis":
        _image_analysis()

    elif app_mode == "Journal Page":
        _journal_page()

    elif app_mode == "Emotional Reports":
        _emotional_report()

