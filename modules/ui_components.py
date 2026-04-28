# modules/ui_components.py

import streamlit as st
from config import COLORS


def render_css():
    """Render all custom CSS"""
    st.markdown("""
        <style>
        /* Main color scheme */
        :root {
            --primary: #FF006E;
            --secondary: #8338EC;
            --accent: #FFBE0B;
            --dark: #1a1a2e;
            --light: #f0f0f0;
        }
        
        /* Animations */
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* Main title */
        .main-title {
            background: linear-gradient(135deg, #FF006E, #8338EC, #FFBE0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            text-align: center;
            margin-bottom: 10px !important;
            animation: slideIn 0.6s ease-out;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1.1rem;
            color: #888;
            margin-bottom: 30px;
            font-weight: 500;
            animation: fadeIn 0.8s ease-out;
        }
        
        /* Section titles */
        .section-title {
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #FF006E, #8338EC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-top: 30px !important;
            margin-bottom: 20px !important;
        }
        
        .sub-section-title {
            font-size: 1.3rem;
            font-weight: 800;
            color: #FF006E;
        }
        
        /* Cards */
        .card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f8ff 100%);
            border-radius: 20px;
            padding: 25px;
            border: 2px solid #f0f0f0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(255, 0, 110, 0.15);
            border-color: #FF006E;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #FF006E15, #8338EC15);
            border-radius: 15px;
            padding: 20px;
            border-left: 4px solid #FF006E;
            text-align: center;
            animation: slideIn 0.5s ease-out;
        }
        
        .metric-card-purple {
            border-left-color: #8338EC;
            background: linear-gradient(135deg, #8338EC15, #FFBE0B15);
        }
        
        .metric-card-gold {
            border-left-color: #FFBE0B;
            background: linear-gradient(135deg, #FFBE0B15, #FF006E15);
        }
        
        .metric-card-green {
            border-left-color: #00D084;
            background: linear-gradient(135deg, #00D08415, #8338EC15);
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stTextInput input {
            border-radius: 15px !important;
            border: 2px solid #e0e0e0 !important;
            font-size: 1rem !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus {
            border-color: #FF006E !important;
            box-shadow: 0 0 0 3px rgba(255, 0, 110, 0.1) !important;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 15px !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            padding: 12px 32px !important;
            border: none !important;
            background: linear-gradient(135deg, #FF006E, #8338EC) !important;
            color: white !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px rgba(255, 0, 110, 0.3) !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(255, 0, 110, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Alerts */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 15px !important;
            padding: 20px !important;
            border-left: 4px solid !important;
            font-weight: 500 !important;
        }
        
        .stSuccess {
            border-left-color: #00D084 !important;
            background-color: #00D08415 !important;
        }
        
        .stInfo {
            border-left-color: #8338EC !important;
            background-color: #8338EC15 !important;
        }
        
        .stError {
            border-left-color: #FF006E !important;
            background-color: #FF006E15 !important;
        }
        
        .stWarning {
            border-left-color: #FFBE0B !important;
            background-color: #FFBE0B15 !important;
        }
        
        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #FF006E, #8338EC, transparent);
            margin: 40px 0 !important;
        }
        
        /* Badges */
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #FF006E, #8338EC);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        
        /* Responsive */
        @media (max-width: 640px) {
            .main-title {
                font-size: 2.5rem !important;
            }
            .section-title {
                font-size: 1.4rem !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with API key inputs"""
    with st.sidebar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ **Setup**")

        st.markdown("**🔑 API Keys**")
        openai_key = st.text_input(
            "OpenAI Key", type="password", placeholder="sk-...", key="openai_sidebar")
        apify_key = st.text_input(
            "Apify Key", type="password", placeholder="apify_...", key="apify_sidebar")
        stripe_key = st.text_input(
            "Stripe Key", type="password", placeholder="sk_test_...", key="stripe_sidebar")

        st.markdown("---")

        st.markdown("""
        **📚 Quick Links**
        - [OpenAI API](https://platform.openai.com/api/keys)
        - [Apify](https://apify.com)
        - [Stripe](https://stripe.com)
        """)

        st.markdown("</div>", unsafe_allow_html=True)

        return openai_key, apify_key, stripe_key


def render_hero():
    """Render hero section"""
    st.markdown('<h1 class="main-title">👥 Influencer Radar</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Deep dive into any influencer • Compare like a pro • Get the tea ☕</p>',
                unsafe_allow_html=True)
    st.markdown("---")


def metric_card(emoji, label, value, subtext=""):
    """Render a single metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #FF006E; margin: 0; font-size: 1.8rem;">{emoji}</h3>
        <p style="font-size: 0.9rem; color: #888; margin: 5px 0 0 0;">{label}</p>
        <p style="font-size: 1.5rem; font-weight: 800; margin: 5px 0; color: #333;">{value}</p>
        {f'<p style="font-size: 0.8rem; color: #666; margin: 5px 0 0 0;">{subtext}</p>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)


def badge(text, color="primary"):
    """Render a badge"""
    colors = {
        "primary": "linear-gradient(135deg, #FF006E, #8338EC)",
        "success": "linear-gradient(135deg, #00D084, #00B873)",
        "warning": "linear-gradient(135deg, #FFBE0B, #FF9F1C)",
    }
    gradient = colors.get(color, colors["primary"])

    st.markdown(f"""
    <span style="display: inline-block; background: {gradient}; color: white; padding: 8px 16px; border-radius: 20px; margin-right: 8px; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem;">{text}</span>
    """, unsafe_allow_html=True)


def info_card(title, emoji, content_dict=None, content_text=None):
    """Render an info card"""
    st.markdown(f"""
    <div class="card">
    <h3 style="color: #FF006E; font-weight: 800; margin-top: 0;">{emoji} {title}</h3>
    """, unsafe_allow_html=True)

    if content_dict:
        for key, value in content_dict.items():
            st.write(f"**{key}:** {value}")
    elif content_text:
        st.write(content_text)

    st.markdown("</div>", unsafe_allow_html=True)


def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 50px;">
        <p>Built with ❤️ | Data from Instagram via Apify | AI Analysis via OpenAI | Payments via Stripe</p>
        <p style="font-size: 0.8rem; color: #aaa;">© 2024 Influencer Radar. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)
