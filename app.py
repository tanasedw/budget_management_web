import streamlit as st
from utils.styles import apply_global_styles

st.set_page_config(
    page_title="Budget Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_global_styles()

st.title("Budget Management")
st.write("Internal OPEX Budget System — Chememan Public Company Limited")
