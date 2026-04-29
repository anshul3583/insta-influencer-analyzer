"""
Helper utility functions
"""
import re
from typing import Tuple


def format_number(number: float, suffix: str = "") -> str:
    """
    Format large numbers with K, M, B suffixes
    
    Args:
        number (float): Number to format
        suffix (str): Optional suffix
        
    Returns:
        str: Formatted number
    """
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B{suffix}"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M{suffix}"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K{suffix}"
    else:
        return f"{number:.0f}{suffix}"


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    
    Args:
        email (str): Email to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return False, "Email cannot be empty"
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, ""


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def get_tier_emoji(tier: str) -> str:
    """
    Get emoji for influencer tier
    
    Args:
        tier (str): Tier name
        
    Returns:
        str: Emoji representation
    """
    tier_map = {
        "a-list": "👑",
        "mega": "⭐",
        "macro": "📢",
        "micro": "📱",
        "nano": "💫"
    }
    return tier_map.get(tier.lower(), "📊")
