"""
Instagram Influencer Analyzer - SaaS Application with Stripe Payments
Main entry point for Streamlit app
Clean, modular architecture with logical separation of concerns
"""

import streamlit as st
from config.settings import UI_CONFIG, CUSTOM_CSS, MESSAGING
from modules.stripe_handler import get_stripe_handler
from modules.persistent_user_manager import PersistentUserManager
from modules.payment_ui import check_and_handle_payment_redirect

# Import page components
from components.header import render_header
from components.sidebar import render_sidebar
from components.footer import render_footer
from pages.single_analysis import render_single_analysis
from pages.comparison import render_comparison
from pages.pricing_info import render_pricing_info

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"]
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize managers
user_manager = PersistentUserManager()

try:
    stripe_handler = get_stripe_handler()
except Exception as e:
    st.error(f"⚠️ Payment system initialization error: {str(e)}")
    st.stop()

# ============================================================================
# PAYMENT VERIFICATION
# ============================================================================

check_and_handle_payment_redirect()

# ============================================================================
# SIDEBAR
# ============================================================================

render_sidebar(user_manager)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
render_header()

# Tabs
tab1, tab2, tab3 = st.tabs([
    MESSAGING["tab_analysis"],
    MESSAGING["tab_comparison"],
    MESSAGING["tab_pricing"]
])

with tab1:
    render_single_analysis(user_manager)

with tab2:
    render_comparison(user_manager)

with tab3:
    render_pricing_info(user_manager)

# ============================================================================
# FOOTER
# ============================================================================

render_footer()
