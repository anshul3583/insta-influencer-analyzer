"""
Single Influencer Analysis page
"""
import streamlit as st
from modules.payment_ui import show_payment_prompt
from modules.analytics import analyze_influencer, validate_username


def render_single_analysis(user_manager):
    """
    Render single influencer analysis tab
    
    Args:
        user_manager: PersistentUserManager instance
    """
    st.header("📊 Single Influencer Analysis")
    st.markdown("""
    Get detailed insights about any Instagram influencer in seconds.
    Powered by real-time data and AI analysis. 🚀
    """)

    # Check access
    can_analyze_free = user_manager.can_perform_free_analysis()
    is_paid = user_manager.is_paid()

    if not can_analyze_free and not is_paid:
        _show_upgrade_prompt()
        return

    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input(
            "Enter Instagram Username",
            placeholder="e.g., cristiano",
            label_visibility="collapsed",
            help="Enter the exact Instagram username (no @ symbol)"
        )
    with col2:
        analyze_button = st.button(
            "🔍 Analyze",
            use_container_width=True,
            type="primary"
        )

    # Validation and analysis
    if analyze_button and username:
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            st.error(f"❌ Invalid username: {error_msg}")
            return

        with st.spinner(f"Analyzing @{username}... This may take a moment ⏳"):
            user_manager.increment_analysis_count()
            result = analyze_influencer(username)

            if result:
                _display_analysis_results(result, user_manager, is_paid)
            else:
                st.error("❌ Failed to analyze influencer. Please try again.")


def _show_upgrade_prompt():
    """Show upgrade prompt for free tier users"""
    st.warning("### 🔒 Upgrade Required")
    st.markdown("""
    Your first analysis was free! Additional analyses cost **$2.99 each**.
    
    **Why upgrade?**
    - ✅ Unlimited analyses
    - ✅ Advanced AI insights
    - ✅ Detailed audience demographics
    - ✅ Growth trend analysis
    """)
    show_payment_prompt(analysis_type="analysis")


def _display_analysis_results(result: dict, user_manager, is_paid: bool):
    """Display analysis results in a beautiful format"""
    
    # Success message
    st.success(f"✅ Analysis Complete for @{result['username']}")
    
    st.markdown("---")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Followers",
            value=result['followers_formatted'],
            delta=f"Growth: {result.get('growth_rate', 'N/A')}%"
        )
    
    with col2:
        st.metric(
            label="Engagement Rate",
            value=result['engagement_rate_formatted'],
            delta="Above Average" if result['engagement_rate'] > 3.5 else "Average"
        )
    
    with col3:
        st.metric(
            label="Audience Quality",
            value=result['quality_stars']
        )
    
    with col4:
        st.metric(
            label="Tier",
            value=result['tier']
        )
    
    st.markdown("---")
    
    # Detailed metrics
    st.subheader("📈 Detailed Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **💰 Sponsorship Value**  
        {result['sponsorship_value_formatted']}
        """)
        st.info(f"""
        **📱 Avg Engagement**  
        {result.get('avg_likes_per_post', 'N/A')} likes per post  
        {result.get('avg_comments_per_post', 'N/A')} comments per post
        """)
    
    with col2:
        st.info(f"""
        **📅 Posting Frequency**  
        {result.get('posting_frequency', 'N/A')}
        """)
        st.info(f"""
        **⏰ Best Time to Post**  
        {result.get('best_posting_time', 'N/A')}
        """)
    
    st.markdown("---")
    
    # Audience demographics
    if result.get('audience_demographics'):
        st.subheader("👥 Audience Demographics")
        
        demo = result['audience_demographics']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Age Range**  \n{demo.get('age_range', 'N/A')}")
        
        with col2:
            st.write(f"**Primary Location**  \n{demo.get('primary_location', 'N/A')}")
        
        with col3:
            interests = ", ".join(demo.get('interests', []))
            st.write(f"**Top Interests**  \n{interests}")
    
    st.markdown("---")
    
    # Upsell for free users
    if not is_paid:
        st.info("""
        ### 💳 Next Analysis?
        You've used your free analysis. Subsequent analyses are **$2.99 each**.
        """)
