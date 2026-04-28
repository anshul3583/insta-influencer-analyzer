"""
Instagram Influencer Analyzer - SaaS Application with Stripe Payments
"""

import streamlit as st
from modules.stripe_handler import get_stripe_handler
from modules.user_manager import UserManager
from modules.payment_ui import show_payment_prompt, check_and_handle_payment_redirect
import urllib.parse

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="👥 Influencer Radar",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .payment-badge {
        background-color: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .free-badge {
        background-color: #2196F3;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize managers
user_manager = UserManager()
try:
    stripe_handler = get_stripe_handler()
except Exception as e:
    st.error(f"⚠️ Payment system initialization error: {str(e)}")
    st.stop()

# ============================================================================
# PAYMENT VERIFICATION ON PAGE LOAD
# ============================================================================

check_and_handle_payment_redirect()

# ============================================================================
# SIDEBAR - USER INFO & STATS
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Your Session")

    # User ID display
    user_id = user_manager.get_user_id()
    st.caption(f"**User ID:** `{user_id[:8]}...`")

    # Payment status badge
    if user_manager.is_paid():
        st.markdown(
            '<div class="payment-badge">✅ PREMIUM MEMBER</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="free-badge">🆓 FREE TIER (1 free analysis)</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Usage statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Analyses Used",
            value=user_manager.get_analysis_count(),
            delta="1 free"
        )
    with col2:
        st.metric(
            label="Comparisons",
            value=user_manager.get_comparison_count()
        )

    st.markdown("---")

    # Payment history
    if user_manager.get_payment_history():
        with st.expander("💳 Payment History"):
            for payment in user_manager.get_payment_history():
                st.write(f"""
                **${payment['amount']}** - {payment['type'].title()}  
                {payment['timestamp'][:10]}  
                Status: {payment['status']}
                """)

    st.markdown("---")

    # Debug info (can be removed in production)
    if st.checkbox("🔍 Debug Info"):
        st.code(f"""
User ID: {user_id}
Analyses: {user_manager.get_analysis_count()}
Comparisons: {user_manager.get_comparison_count()}
Is Paid: {user_manager.is_paid()}
Session: {user_manager.get_session_summary()}
        """)

# ============================================================================
# MAIN HEADER
# ============================================================================

st.title("👥 Influencer Radar")
st.markdown(
    "*Deep dive into any influencer • Compare like a pro • Get the tea ☕*")
st.markdown("---")

# ============================================================================
# TABS SETUP
# ============================================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Single Analysis",
    "🔄 Comparison",
    "ℹ️ Pricing & Info"
])

# ============================================================================
# TAB 1: SINGLE INFLUENCER ANALYSIS
# ============================================================================

with tab1:
    st.header("📊 Single Influencer Analysis")
    st.write("Get detailed insights about any Instagram influencer")

    # Check if user can perform analysis
    can_analyze_free = user_manager.can_perform_free_analysis()
    is_paid = user_manager.is_paid()

    if not can_analyze_free and not is_paid:
        st.warning("### 🔒 Upgrade Required")
        st.write(
            "Your first analysis was free! Additional analyses cost **$2.99 each**.")
        show_payment_prompt(analysis_type="analysis")
        st.stop()

    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input(
            "Enter Instagram Username",
            placeholder="e.g., cristiano",
            label_visibility="collapsed"
        )
    with col2:
        analyze_button = st.button("🔍 Analyze", use_container_width=True)

    if analyze_button and username:
        st.info(f"Analyzing @{username}... This may take a moment ⏳")

        # Mark that user performed an analysis
        user_manager.increment_analysis_count()

        # PLACEHOLDER: Call your existing analysis functions here
        # This is where you integrate with your Apify + OpenAI code

        st.success(f"""
        ### ✅ Analysis Complete for @{username}
        
        **Engagement Rate:** 4.2%  
        **Follower Count:** 120.5M  
        **Audience Quality:** ⭐⭐⭐⭐⭐  
        **Tier:** A-List Celebrity  
        **Estimated Sponsorship Value:** $50,000 - $100,000 per post  
        
        *This is a placeholder. Replace with your actual Apify + OpenAI analysis.*
        """)

        # Show payment upsell for next analysis
        if not is_paid:
            st.info(f"""
            ### 💳 Next Analysis?
            You've used your free analysis. Subsequent analyses are **$2.99 each**.
            """)

# ============================================================================
# TAB 2: INFLUENCER COMPARISON
# ============================================================================

with tab2:
    st.header("🔄 Influencer Comparison")
    st.write("Compare two influencers side-by-side")

    # Check if user has access to comparisons
    if not user_manager.can_perform_comparison():
        st.warning("### 🔒 Premium Feature")
        st.write(
            "Comparisons are **only available to paying members** ($4.99 per comparison).")
        show_payment_prompt(analysis_type="comparison")
        st.stop()

    # Comparison input
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        username1 = st.text_input(
            "First Instagram Username",
            placeholder="e.g., cristiano",
            key="user1"
        )
    with col2:
        st.write("")  # Spacer
        st.write("vs")
    with col3:
        username2 = st.text_input(
            "Second Instagram Username",
            placeholder="e.g., messi",
            key="user2"
        )

    compare_button = st.button("⚡ Compare Now", use_container_width=True)

    if compare_button and username1 and username2:
        if username1.lower() == username2.lower():
            st.error("❌ Please enter two different usernames!")
        else:
            st.info(f"Comparing @{username1} vs @{username2}... ⏳")

            # Mark comparison
            user_manager.increment_comparison_count()

            # PLACEHOLDER: Call your existing comparison functions
            st.success(f"""
            ### ✅ Comparison Complete
            
            **Influencer 1: @{username1}**  
            Followers: 120.5M | Engagement: 4.2% | Tier: A-List
            
            **Influencer 2: @{username2}**  
            Followers: 105.3M | Engagement: 3.8% | Tier: A-List
            
            **Winner:** @{username1} by engagement metrics
            
            *This is a placeholder. Replace with your actual comparison logic.*
            """)

# ============================================================================
# TAB 3: PRICING & INFO
# ============================================================================

with tab3:
    st.header("💳 Pricing & Information")

    pricing_data = {
        "Feature": [
            "Single Influencer Analysis",
            "Influencer Comparison",
            "AI-Powered Insights (GPT-4)",
            "Engagement Metrics",
            "Audience Quality Score",
            "Sponsorship Value Estimate"
        ],
        "Free Tier": [
            "1 Free",
            "❌ Locked",
            "✅",
            "✅",
            "✅",
            "✅"
        ],
        "Premium": [
            "$2.99 each",
            "$4.99 each",
            "✅",
            "✅",
            "✅",
            "✅"
        ]
    }

    st.dataframe(pricing_data, use_container_width=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="First Analysis", value="Free", delta="Forever")

    with col2:
        st.metric(label="Per Analysis", value="$2.99")

    with col3:
        st.metric(label="Per Comparison", value="$4.99")

    st.markdown("---")

    st.subheader("❓ FAQ")

    with st.expander("How does the free tier work?"):
        st.write("""
        Your **first analysis is completely free**! You get to try out the app and 
        see the quality of insights. After that, each additional analysis costs $2.99.
        """)

    with st.expander("Are comparisons worth it?"):
        st.write("""
        Comparisons use our advanced GPT-4 model to provide **side-by-side analysis** 
        of two influencers, including growth trajectories, audience overlap, and 
        engagement trends. Perfect for brand partnerships and competitor analysis.
        """)

    with st.expander("How long does analysis take?"):
        st.write("""
        Typically **15-30 seconds** depending on the influencer's follower count 
        and Instagram API response times.
        """)

    with st.expander("Can I get a refund?"):
        st.write("""
        Yes! Contact us at support@influencerradar.app within 24 hours of purchase 
        for a full refund.
        """)

    st.markdown("---")

    if user_manager.is_paid():
        st.success(
            "✅ **You're a Premium Member!** Enjoy unlimited analyses and comparisons.")
    else:
        st.info("""
        ### Unlock Premium Features
        
        Get access to unlimited analyses and comparisons for just $2.99-$4.99 per action.
        Your first analysis is free to get started!
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px;">
    <p>Influencer Radar © 2026 | Powered by GPT-4 & Apify API</p>
    <p><a href="mailto:support@influencerradar.app">Support</a> • 
    <a href="#">Privacy Policy</a> • 
    <a href="#">Terms of Service</a></p>
</div>
""", unsafe_allow_html=True)
