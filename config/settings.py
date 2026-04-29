"""
Configuration and settings for Influencer Radar
"""
"""
Configuration and settings for Influencer Radar
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================
COLORS = {
    "primary": "#FF6B6B",
    "secondary": "#4ECDC4",
    "success": "#51CF66",
    "warning": "#FFD43B",
    "danger": "#FF6B6B",
    "info": "#339AF0",
    "light": "#F8F9FA",
    "dark": "#2C3E50",
    "text": "#31333F",
    "text_light": "#72757E",
    "background": "#FFFFFF",
    "background_secondary": "#F0F2F6",
    "border": "#E1E4E8",
    # Badges
    "badge_success": "#4CAF50",
    "badge_info": "#2196F3",
    "badge_warning": "#FF9800",
    "badge_danger": "#F44336",
    # Gradients
    "gradient_start": "#FF6B6B",
    "gradient_end": "#4ECDC4",
}

# ============================================================================
# PRICING
# ============================================================================
PRICING = {
    "analysis": 2.99,
    "comparison": 4.99,
    "free_analyses": 1,
    "free_comparisons": 0
}

# ... rest of your settings.py file

# ============================================================================
# PRICING
# ============================================================================
PRICING = {
    "analysis": 2.99,
    "comparison": 4.99,
    "free_analyses": 1,
    "free_comparisons": 0
}

# ============================================================================
# FEATURE ACCESS
# ============================================================================
FEATURES = {
    "single_analysis": {
        "free": 1,
        "premium": "unlimited"
    },
    "comparison": {
        "free": False,
        "premium": True
    }
}

# ============================================================================
# UI MESSAGING
# ============================================================================
MESSAGING = {
    "app_title": "👥 Influencer Radar",
    "app_subtitle": "*Deep dive into any influencer • Compare like a pro • Get the tea ☕*",
    "tab_analysis": "📊 Single Analysis",
    "tab_comparison": "🔄 Comparison",
    "tab_pricing": "ℹ️ Pricing & Info",
}

# ============================================================================
# CUSTOM CSS
# ============================================================================
CUSTOM_CSS = """
    <style>
    .payment-badge {
        background-color: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 0;
    }
    .free-badge {
        background-color: #2196F3;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 0;
    }
    .info-card {
        background-color: #f0f2f6;
        border-left: 4px solid #0066cc;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .success-card {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
"""

# ============================================================================
# FAQ CONTENT
# ============================================================================
FAQ_CONTENT = {
    "How does the free tier work?": """
        Your **first analysis is completely free**! You get to try out the app and 
        see the quality of insights. After that, each additional analysis costs **$2.99**.
    """,
    "Are comparisons worth it?": """
        Comparisons use our advanced GPT-4 model to provide **side-by-side analysis** 
        of two influencers, including growth trajectories, audience overlap, and 
        engagement trends. Perfect for brand partnerships and competitor analysis.
    """,
    "How long does analysis take?": """
        Typically **15-30 seconds** depending on the influencer's follower count 
        and Instagram API response times.
    """,
    "Can I get a refund?": """
        Yes! Contact us at support@influencerradar.app within **24 hours** of purchase 
        for a full refund.
    """,
    "What data sources do you use?": """
        We use **Apify API** for Instagram data collection and **OpenAI GPT-4** 
        for intelligent analysis and insights generation.
    """,
    "Is my data private?": """
        Yes! All data is **encrypted** and we never share user information with third parties.
        We comply with GDPR and privacy regulations.
    """
}

# ============================================================================
# API CONFIGURATION
# ============================================================================
# These should be loaded from environment variables
API_CONFIG = {
    "apify": {
        "timeout": 30,
        "retry_attempts": 3
    },
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7
    }
}

# ============================================================================
# UI CONFIGURATION
# ============================================================================
UI_CONFIG = {
    "page_title": "👥 Influencer Radar",
    "page_icon": "👥",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
