"""
Sidebar component with user info and stats
"""
import streamlit as st
from modules.persistent_user_manager import show_persistent_debug_panel


def render_sidebar(user_manager):
    """
    Render sidebar with user info, stats, and debug options
    
    Args:
        user_manager: PersistentUserManager instance
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Your Session")

        # User ID display
        user_id = user_manager.get_user_id()
        st.caption(f"**User ID:** `{user_id[:8]}...`")

        # Payment status badge
        _render_payment_badge(user_manager)

        st.markdown("---")

        # Usage statistics
        _render_usage_stats(user_manager)

        st.markdown("---")

        # Payment history
        _render_payment_history(user_manager)

        st.markdown("---")

        # Debug sections
        _render_debug_section(user_manager, user_id)


def _render_payment_badge(user_manager):
    """Render payment status badge"""
    if user_manager.is_paid():
        st.markdown(
            '<div class="payment-badge">✅ PREMIUM MEMBER</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="free-badge">🆓 FREE TIER (1 free analysis)</div>',
            unsafe_allow_html=True
        )


def _render_usage_stats(user_manager):
    """Render usage statistics"""
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


def _render_payment_history(user_manager):
    """Render payment history if available"""
    payment_history = user_manager.get_payment_history()
    if payment_history:
        with st.expander("💳 Payment History"):
            for payment in payment_history:
                st.write(f"""
                **${payment['amount']}** - {payment['type'].title()}  
                {payment['timestamp'][:10]}  
                Status: {payment['status']}
                """)


def _render_debug_section(user_manager, user_id):
    """Render debug information sections"""
    if st.checkbox("🔍 Debug Info"):
        st.code(f"""
User ID: {user_id}
Browser ID: {user_manager.get_browser_id()[:8]}...
Analyses: {user_manager.get_analysis_count()}
Comparisons: {user_manager.get_comparison_count()}
Is Paid: {user_manager.is_paid()}
Storage: ✅ Persistent (Hybrid)
Session: {user_manager.get_session_summary()}
        """)

    if st.checkbox("🔧 Storage Debug"):
        show_persistent_debug_panel()
