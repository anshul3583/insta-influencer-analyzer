# config.py

# App Configuration
APP_TITLE = "Influencer Radar"
APP_DESCRIPTION = "Deep dive into any influencer • Compare like a pro • Get the tea ☕"
APP_ICON = "👥"

# Color scheme
COLORS = {
    "primary": "#FF006E",      # Hot pink
    "secondary": "#8338EC",    # Purple
    "accent": "#FFBE0B",       # Yellow
    "success": "#00D084",      # Green
    "dark": "#1a1a2e",         # Dark background
    "light": "#f0f0f0",        # Light background
}

# API Configuration
API_TIMEOUTS = {
    "apify": 60,               # 60 seconds for Apify
    "openai": 30,              # 30 seconds for OpenAI
}

# Pricing
PRICING = {
    "basic_analysis": 0.00,
    "premium_report": 9.99,
    "pro_monthly": 29.99,
}

# Limits
LIMITS = {
    "free_analyses_per_day": 1,
    "max_competitors_compare": 5,
}
