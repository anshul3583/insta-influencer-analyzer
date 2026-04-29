"""
Pricing and Information page
"""
import streamlit as st
from config.settings import PRICING, FAQ_CONTENT


def render_pricing_info(user_manager):
    """
    Render pricing and information tab
    
    Args:
        user_manager: PersistentUserManager instance
    """
    st.header("💳 Pricing & Information")
    st.markdown("Find the perfect plan for your needs")
    
    st.markdown("---")
    
    # Pricing table
    _render_pricing_table()
    
    st.markdown("---")
    
    # Price highlights
    _render_price_metrics()
    
    st.markdown("---")
    
    # FAQ
    _render_faq()
    
    st.markdown("---")
    
    # User status message
    _render_user_status(user_manager)


def _render_pricing_table():
    """Render pricing comparison table"""
    st.subheader("Feature Comparison")
    
    pricing_data = {
        "Feature": [
            "Single Influencer Analysis",
            "Influencer Comparison",
            "AI-Powered Insights (GPT-4)",
            "Engagement Metrics",
            "Audience Quality Score",
            "Sponsorship Value Estimate",
            "Growth Analysis",
            "Audience Demographics",
            "Priority Support"
        ],
        "Free Tier": [
            "1 Analysis",
            "❌",
            "✅",
            "✅",
            "✅",
            "✅",
            "❌",
            "❌",
            "❌"
        ],
        "Premium ($2.99-$4.99)": [
            "Unlimited",
            "✅",
            "✅",
            "✅",
            "✅",
            "✅",
            "✅",
            "✅",
            "✅"
        ]
    }
    
    st.dataframe(pricing_data, use_container_width=True, hide_index=True)


def _render_price_metrics():
    """Render price metrics in columns"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="First Analysis",
            value="Free",
            delta="Forever included"
        )
    
    with col2:
        st.metric(
            label="Per Analysis",
            value=f"${PRICING['analysis']}",
            delta="Quick & Reliable"
        )
    
    with col3:
        st.metric(
            label="Per Comparison",
            value=f"${PRICING['comparison']}",
            delta="Premium Feature"
        )


def _render_faq():
    """Render FAQ section"""
    st.subheader("❓ Frequently Asked Questions")
    
    for question, answer in FAQ_CONTENT.items():
        with st.expander(question):
            st.markdown(answer)


def _render_user_status(user_manager):
    """Render user status message"""
    st.subheader("Your Status")
    
    if user_manager.is_paid():
        st.success(
            "✅ **You're a Premium Member!**  \n"
            "Enjoy unlimited analyses and comparisons."
        )
    else:
        st.info("""
        ### 🚀 Unlock Premium Features
        
        Get access to unlimited analyses and comparisons for just **$2.99-$4.99** per action.
        
        Your first analysis is **completely free** to get started!
        """)
