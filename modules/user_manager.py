"""User session management and usage tracking."""
import streamlit as st
from datetime import datetime
from typing import Dict, List


class UserManager:
    """Manages user session state, usage tracking, and payment status."""

    def __init__(self):
        """Initialize user session in Streamlit state."""
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state variables if they don't exist."""
        defaults = {
            "user_id": self._generate_user_id(),
            "analyses_count": 0,
            "comparisons_count": 0,
            "is_paid_user": False,
            "payment_history": [],
            "session_start": datetime.now(),
            "last_payment_session_id": None
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def _generate_user_id() -> str:
        """Generate a unique user ID based on session."""
        import hashlib
        import time
        user_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        return f"user_{user_hash}"

    def get_user_id(self) -> str:
        """Get current user ID."""
        return st.session_state.user_id

    def increment_analysis_count(self):
        """Increment analysis count by 1."""
        st.session_state.analyses_count += 1

    def increment_comparison_count(self):
        """Increment comparison count by 1."""
        st.session_state.comparisons_count += 1

    def get_analysis_count(self) -> int:
        """Get total analyses performed."""
        return st.session_state.analyses_count

    def get_comparison_count(self) -> int:
        """Get total comparisons performed."""
        return st.session_state.comparisons_count

    def set_paid_user(self, status: bool):
        """Mark user as paid."""
        st.session_state.is_paid_user = status

    def is_paid(self) -> bool:
        """Check if user has paid."""
        return st.session_state.is_paid_user

    def add_payment_record(self, payment_id: str, amount: float,
                           payment_type: str, status: str = "completed"):
        """Record a payment transaction."""
        payment_record = {
            "payment_id": payment_id,
            "amount": amount,
            "type": payment_type,  # "analysis" or "comparison"
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.payment_history.append(payment_record)

    def get_payment_history(self) -> List[Dict]:
        """Get user's payment history."""
        return st.session_state.payment_history

    def can_perform_free_analysis(self) -> bool:
        """Check if user qualifies for free analysis (1st analysis free)."""
        return self.get_analysis_count() == 0

    def can_perform_comparison(self) -> bool:
        """Check if user can perform comparison (must be paid)."""
        return self.is_paid()

    def set_last_payment_session(self, session_id: str):
        """Store last payment session ID for verification."""
        st.session_state.last_payment_session_id = session_id

    def get_last_payment_session(self) -> str:
        """Get last payment session ID."""
        return st.session_state.last_payment_session_id

    def get_session_summary(self) -> Dict:
        """Get summary of user's current session."""
        return {
            "user_id": self.get_user_id(),
            "analyses_performed": self.get_analysis_count(),
            "comparisons_performed": self.get_comparison_count(),
            "is_paid": self.is_paid(),
            "total_spent": sum(p["amount"] for p in self.get_payment_history()),
            "session_duration": (datetime.now() - st.session_state.session_start).total_seconds()
        }

    def reset_session(self):
        """Reset all user data (for testing only)."""
        for key in ["analyses_count", "comparisons_count", "is_paid_user",
                    "payment_history", "last_payment_session_id"]:
            if key in st.session_state:
                del st.session_state[key]
        self._init_session_state()
