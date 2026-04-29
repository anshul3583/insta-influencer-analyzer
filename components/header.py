"""
Header component for Influencer Radar
"""
import streamlit as st
from config.settings import MESSAGING

def render_header():
    """Render the main header"""
    st.title(MESSAGING["app_title"])
    st.markdown(MESSAGING["app_subtitle"])
    st.markdown("---")
