"""
Influencer Comparison page
"""
import streamlit as st
from modules.payment_ui import show_payment_prompt
from modules.analytics import compare_influencers, validate_username


def render_comparison(user_manager):
    """
    Render influencer comparison tab
    
    Args:
        user_manager: PersistentUserManager instance
    """
    st.header("🔄 Influencer Comparison")
    st.markdown("""
    Compare two influencers side-by-side with detailed metrics.
    Find the perfect match for your brand partnership. 🎯
    """)

    # Check if user has access
    if not user_manager.can_perform_comparison():
        _show_premium_lock()
        return

    # Input section with better UX
    st.subheader("Select Two Influencers to Compare")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        username1 = st.text_input(
            "First Instagram Username",
            placeholder="e.g., cristiano",
            key="user1",
            help="Enter the first influencer's username"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("**VS**")
    
    with col3:
        username2 = st.text_input(
            "Second Instagram Username",
            placeholder="e.g., messi",
            key="user2",
            help="Enter the second influencer's username"
        )

    compare_button = st.button(
        "⚡ Compare Now",
        use_container_width=True,
        type="primary"
    )

    # Validation and comparison
    if compare_button and username1 and username2:
        # Validate both usernames
        is_valid1, error_msg1 = validate_username(username1)
        is_valid2, error_msg2 = validate_username(username2)
        
        if not is_valid1:
            st.error(f"❌ Invalid first username: {error_msg1}")
            return
        
        if not is_valid2:
            st.error(f"❌ Invalid second username: {error_msg2}")
            return

        if username1.lower() == username2.lower():
            st.error("❌ Please enter two different usernames!")
            return

        with st.spinner(f"Comparing @{username1} vs @{username2}... ⏳"):
            user_manager.increment_comparison_count()
            result = compare_influencers(username1, username2)

            if result:
                _display_comparison_results(result)
            else:
                st.error("❌ Failed to compare influencers. Please try again.")


def _show_premium_lock():
    """Show premium feature lock"""
    st.warning("### 🔒 Premium Feature")
    st.markdown("""
    Comparisons are **exclusive to Premium members** at **$4.99 per comparison**.
    
    **What you get:**
    - 📊 Side-by-side comparison
    - 📈 Growth trajectory analysis
    - 👥 Audience overlap insights
    - 💰 Sponsorship value comparison
    - 🎯 Brand fit analysis
    """)
    show_payment_prompt(analysis_type="comparison")


def _display_comparison_results(result: dict):
    """Display comparison results in a beautiful side-by-side format"""
    
    st.success("✅ Comparison Complete!")
    st.markdown("---")
    
    # Side-by-side comparison
    col1, col2 = st.columns(2)
    
    user1 = result['user1']
    user2 = result['user2']
    
    with col1:
        st.subheader(f"@{user1['username']}")
        st.metric("Followers", user1['followers'])
        st.metric("Engagement Rate", f"{user1['engagement']}%")
        st.metric("Tier", user1['tier'])
        st.metric("Est. Sponsorship Value", user1['sponsorship_value'])
    
    with col2:
        st.subheader(f"@{user2['username']}")
        st.metric("Followers", user2['followers'])
        st.metric("Engagement Rate", f"{user2['engagement']}%")
        st.metric("Tier", user2['tier'])
        st.metric("Est. Sponsorship Value", user2['sponsorship_value'])
    
    st.markdown("---")
    
    # Winner announcement
    winner = result['winner']
    reason = result['winner_reason']
    
    st.success(f"""
    ### 🏆 Winner: @{winner}
    **Reason:** {reason}
    """)
    
    st.markdown("---")
    
    # Detailed metrics comparison
    st.subheader("📊 Metrics Breakdown")
    
    metrics_comp = result.get('metrics_comparison', {})
    
    comparison_table = {
        "Metric": ["Followers", "Engagement", "Growth Rate", "Audience Quality"],
        "Winner": [
            "🥇 " + metrics_comp.get('followers_winner', 'N/A'),
            "🥇 " + metrics_comp.get('engagement_winner', 'N/A'),
            "🥇 " + metrics_comp.get('growth_winner', 'N/A'),
            "🥇 " + metrics_comp.get('audience_quality_winner', 'N/A'),
        ]
    }
    
    st.dataframe(comparison_table, use_container_width=True, hide_index=True)
