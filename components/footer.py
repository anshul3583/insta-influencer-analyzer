"""
Footer component
"""
import streamlit as st


def render_footer():
    """Render the app footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px;">
        <p><strong>Influencer Radar © 2026</strong> | Powered by GPT-4 & Apify API</p>
        <p>
            <a href="mailto:support@influencerradar.app">📧 Support</a> • 
            <a href="https://example.com/privacy">🔒 Privacy</a> • 
            <a href="https://example.com/terms">⚖️ Terms</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
