"""
Hybrid session + local storage persistence manager for user data.
Enables no-login required analytics with data persisting across browser sessions.

Architecture:
- Browser fingerprinting: Generate consistent user_id for same browser/device
- Storage layers: Query params → session state → fallback
- Migration: Preserve old session data when user returns
- Error handling: Graceful degradation if persistence fails
"""

import streamlit as st
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import base64
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class BrowserFingerprint:
    """Generate and manage browser fingerprint for consistent user identification."""

    @staticmethod
    def generate_fingerprint() -> str:
        """
        Generate a browser fingerprint for consistent user identification.

        Uses:
        - Query params (browser can pass unique identifier)
        - Timestamp (but deterministically hashed for consistency)
        - System info available to Streamlit
        """
        try:
            # Try to get from query params first (most reliable)
            query_params = st.query_params
            if "browser_id" in query_params:
                browser_id = query_params["browser_id"]
                logger.debug(f"Using browser_id from query params: {browser_id[:8]}...")
                return browser_id

            # Fall back to generating a fingerprint
            fingerprint_data = {
                "session_id": st.session_state.get("_streamlit_session_id", "unknown"),
                "url": st.session_state.get("_streamlit_script", "unknown"),
            }

            fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
            browser_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
            logger.debug(f"Generated fingerprint: {browser_hash}")
            return browser_hash

        except Exception as e:
            logger.warning(f"Error generating fingerprint: {e}")
            # Emergency fallback: use session ID
            return hashlib.md5(
                str(st.session_state.get("_streamlit_session_id", "emergency")).encode()
            ).hexdigest()[:16]

    @staticmethod
    def get_or_create_browser_id() -> str:
        """Get browser ID, creating it if necessary and storing in query params."""
        if "_browser_id" not in st.session_state:
            browser_id = BrowserFingerprint.generate_fingerprint()
            st.session_state._browser_id = browser_id

            # Update query params for next page load
            params = st.query_params
            params["browser_id"] = browser_id
            st.query_params.clear()
            st.query_params.update(params)

            logger.info(f"Created new browser ID: {browser_id[:8]}...")

        return st.session_state._browser_id


class LocalStorageSimulator:
    """
    Simulate browser localStorage using Streamlit's caching and query params.
    Provides persistent storage across browser sessions.
    """

    STORAGE_PREFIX = "influencer_analyzer_"
    CACHE_DIR = Path.home() / ".influencer_analyzer_cache"

    @staticmethod
    def _get_storage_key(browser_id: str, data_key: str) -> str:
        """Get full storage key for this browser and data."""
        return f"{LocalStorageSimulator.STORAGE_PREFIX}{browser_id}_{data_key}"

    @staticmethod
    def set_item(browser_id: str, key: str, value: Any) -> bool:
        """
        Store value in persistent storage.

        Try multiple backends:
        1. Streamlit session state (fast, current session)
        2. Query params (survives page reload)
        3. Local filesystem (localhost only)
        """
        try:
            storage_key = LocalStorageSimulator._get_storage_key(browser_id, key)

            # Primary: session state
            st.session_state[storage_key] = value

            # Secondary: try filesystem storage (localhost friendly)
            try:
                if LocalStorageSimulator.CACHE_DIR.exists() or not is_streamlit_cloud():
                    LocalStorageSimulator._filesystem_set(browser_id, key, value)
            except Exception as e:
                logger.debug(f"Filesystem storage failed (non-critical): {e}")

            logger.debug(f"Stored {key} in session state")
            return True

        except Exception as e:
            logger.error(f"Error setting item {key}: {e}")
            return False

    @staticmethod
    def get_item(browser_id: str, key: str) -> Optional[Any]:
        """
        Retrieve value from persistent storage.

        Try multiple backends:
        1. Session state
        2. Filesystem cache
        """
        try:
            storage_key = LocalStorageSimulator._get_storage_key(browser_id, key)

            # Check session state first
            if storage_key in st.session_state:
                logger.debug(f"Retrieved {key} from session state")
                return st.session_state[storage_key]

            # Try filesystem
            value = LocalStorageSimulator._filesystem_get(browser_id, key)
            if value is not None:
                logger.debug(f"Retrieved {key} from filesystem, syncing to session")
                st.session_state[storage_key] = value
                return value

            return None

        except Exception as e:
            logger.warning(f"Error getting item {key}: {e}")
            return None

    @staticmethod
    def _filesystem_set(browser_id: str, key: str, value: Any) -> bool:
        """Store to local filesystem (localhost only)."""
        try:
            if is_streamlit_cloud():
                return False

            LocalStorageSimulator.CACHE_DIR.mkdir(exist_ok=True)
            cache_file = (
                LocalStorageSimulator.CACHE_DIR /
                f"{browser_id}_{key}.json"
            )

            with open(cache_file, 'w') as f:
                json.dump(value, f)

            logger.debug(f"Stored {key} to filesystem: {cache_file}")
            return True
        except Exception as e:
            logger.debug(f"Filesystem store failed: {e}")
            return False

    @staticmethod
    def _filesystem_get(browser_id: str, key: str) -> Optional[Any]:
        """Retrieve from local filesystem."""
        try:
            if is_streamlit_cloud():
                return None

            cache_file = (
                LocalStorageSimulator.CACHE_DIR /
                f"{browser_id}_{key}.json"
            )

            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(f"Filesystem get failed: {e}")

        return None

    @staticmethod
    def remove_item(browser_id: str, key: str) -> bool:
        """Remove value from persistent storage."""
        try:
            storage_key = LocalStorageSimulator._get_storage_key(browser_id, key)
            if storage_key in st.session_state:
                del st.session_state[storage_key]

            # Also remove from filesystem
            try:
                cache_file = (
                    LocalStorageSimulator.CACHE_DIR /
                    f"{browser_id}_{key}.json"
                )
                cache_file.unlink(missing_ok=True)
            except Exception:
                pass

            return True
        except Exception as e:
            logger.error(f"Error removing item {key}: {e}")
            return False

    @staticmethod
    def clear_all_for_browser(browser_id: str) -> bool:
        """Clear all stored data for a browser."""
        try:
            # Clear session state
            keys_to_delete = [
                k for k in st.session_state.keys()
                if k.startswith(
                    LocalStorageSimulator._get_storage_key(browser_id, "")
                )
            ]
            for key in keys_to_delete:
                del st.session_state[key]

            # Clear filesystem
            try:
                for cache_file in LocalStorageSimulator.CACHE_DIR.glob(
                    f"{browser_id}_*.json"
                ):
                    cache_file.unlink()
            except Exception:
                pass

            logger.info(f"Cleared all storage for browser {browser_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
            return False


class PersistentUserManager:
    """
    Manages user data with hybrid persistence (session + local storage).

    Features:
    - No login required
    - Consistent user ID across browser sessions
    - Automatic data persistence
    - Migration from old sessions
    - Graceful degradation on storage failures
    - Debug utilities
    """

    # Data schema version for migrations
    DATA_VERSION = 1

    def __init__(self):
        """Initialize persistent user manager."""
        self.browser_id = BrowserFingerprint.get_or_create_browser_id()
        self.storage = LocalStorageSimulator

        logger.info(f"PersistentUserManager initialized for browser: {self.browser_id[:8]}...")

        # Initialize data structure
        self._init_user_data()

        # Perform any necessary migrations
        self._perform_migrations()

    def _init_user_data(self):
        """Initialize user data if not already present."""
        try:
            user_data = self.storage.get_item(self.browser_id, "user_data")

            if user_data is None:
                # First time - create new user data
                user_data = {
                    "version": self.DATA_VERSION,
                    "user_id": self._generate_persistent_user_id(),
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat(),
                    "analyses_count": 0,
                    "comparisons_count": 0,
                    "is_paid_user": False,
                    "payment_history": [],
                    # Email verification fields
                    "email": None,
                    "is_email_verified": False,
                    "email_verified_at": None,
                }
                self.storage.set_item(self.browser_id, "user_data", user_data)
                logger.info(f"Created new user data for {self.browser_id[:8]}...")
            else:
                # Update last_accessed
                user_data["last_accessed"] = datetime.now().isoformat()
                self.storage.set_item(self.browser_id, "user_data", user_data)
                logger.info(f"Loaded existing user data for {self.browser_id[:8]}...")

            # Sync to session state for fast access
            st.session_state._persistent_user_data = user_data

        except Exception as e:
            logger.error(f"Error initializing user data: {e}")
            # Create minimal fallback data
            st.session_state._persistent_user_data = {
                "version": self.DATA_VERSION,
                "user_id": self._generate_persistent_user_id(),
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "analyses_count": 0,
                "comparisons_count": 0,
                "is_paid_user": False,
                "payment_history": [],
            }

    def _perform_migrations(self):
        """Handle data structure migrations and old session data."""
        try:
            # Check for old session data (from previous non-persistent sessions)
            old_data_key = "legacy_user_sessions"
            old_sessions = self.storage.get_item(self.browser_id, old_data_key)

            if old_sessions is None and "user_id" in st.session_state:
                # Migrate old session data if it exists
                logger.info("Attempting to migrate legacy session data...")

                current_data = st.session_state._persistent_user_data

                # Preserve any higher counts
                if st.session_state.get("analyses_count", 0) > current_data["analyses_count"]:
                    current_data["analyses_count"] = st.session_state["analyses_count"]
                    logger.debug("Migrated analyses_count from legacy session")

                if st.session_state.get("comparisons_count", 0) > current_data["comparisons_count"]:
                    current_data["comparisons_count"] = st.session_state["comparisons_count"]
                    logger.debug("Migrated comparisons_count from legacy session")

                if st.session_state.get("is_paid_user", False) and not current_data["is_paid_user"]:
                    current_data["is_paid_user"] = True
                    logger.debug("Migrated is_paid_user from legacy session")

                if st.session_state.get("payment_history", []) and not current_data["payment_history"]:
                    current_data["payment_history"] = st.session_state["payment_history"]
                    logger.debug("Migrated payment_history from legacy session")

                # Save migrated data
                self.storage.set_item(self.browser_id, "user_data", current_data)
                st.session_state._persistent_user_data = current_data

                # Mark migration as done
                self.storage.set_item(self.browser_id, old_data_key, True)

        except Exception as e:
            logger.warning(f"Migration error (non-critical): {e}")

    def _generate_persistent_user_id(self) -> str:
        """Generate a persistent user ID based on browser."""
        try:
            # Use browser_id as base for consistency
            user_id_hash = hashlib.sha256(
                f"{self.browser_id}:{datetime.now().date()}".encode()
            ).hexdigest()[:12]
            return f"user_{user_id_hash}"
        except Exception as e:
            logger.error(f"Error generating user ID: {e}")
            return f"user_{hashlib.md5(self.browser_id.encode()).hexdigest()[:8]}"

    def _get_user_data(self) -> Dict:
        """Get current user data, ensuring consistency."""
        if "_persistent_user_data" not in st.session_state:
            self._init_user_data()

        return st.session_state._persistent_user_data

    def _save_user_data(self):
        """Save user data to persistent storage."""
        try:
            data = self._get_user_data()
            data["last_accessed"] = datetime.now().isoformat()
            self.storage.set_item(self.browser_id, "user_data", data)
            st.session_state._persistent_user_data = data
        except Exception as e:
            logger.error(f"Error saving user data: {e}")

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def get_user_id(self) -> str:
        """Get persistent user ID."""
        return self._get_user_data()["user_id"]

    def get_browser_id(self) -> str:
        """Get browser fingerprint ID (for debugging)."""
        return self.browser_id

    def get_analysis_count(self) -> int:
        """Get total analyses performed."""
        return self._get_user_data()["analyses_count"]

    def get_comparison_count(self) -> int:
        """Get total comparisons performed."""
        return self._get_user_data()["comparisons_count"]

    def increment_analysis_count(self):
        """Increment analysis count."""
        data = self._get_user_data()
        data["analyses_count"] += 1
        self._save_user_data()
        logger.debug(f"Incremented analyses to {data['analyses_count']}")

    def increment_comparison_count(self):
        """Increment comparison count."""
        data = self._get_user_data()
        data["comparisons_count"] += 1
        self._save_user_data()
        logger.debug(f"Incremented comparisons to {data['comparisons_count']}")

    def set_paid_user(self, status: bool):
        """Mark user as paid."""
        data = self._get_user_data()
        data["is_paid_user"] = status
        self._save_user_data()
        logger.info(f"Updated paid status: {status}")

    def is_paid(self) -> bool:
        """Check if user has paid."""
        return self._get_user_data()["is_paid_user"]

    def add_payment_record(
        self,
        payment_id: str,
        amount: float,
        payment_type: str,
        status: str = "completed"
    ):
        """Record a payment transaction."""
        data = self._get_user_data()
        payment_record = {
            "payment_id": payment_id,
            "amount": amount,
            "type": payment_type,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        data["payment_history"].append(payment_record)
        self._save_user_data()
        logger.info(f"Added payment record: {payment_id}")

    def get_payment_history(self) -> List[Dict]:
        """Get user's payment history."""
        return self._get_user_data()["payment_history"]

    def can_perform_free_analysis(self) -> bool:
        """Check if user qualifies for free analysis."""
        return self.get_analysis_count() == 0

    def can_perform_comparison(self) -> bool:
        """Check if user can perform comparison."""
        return self.is_paid()

    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================

    def set_verified_email(self, email: str):
        """Mark email as verified and link to user."""
        data = self._get_user_data()
        data["email"] = email
        data["is_email_verified"] = True
        data["email_verified_at"] = datetime.now().isoformat()
        self._save_user_data()
        logger.info(f"Email verified for user: {email}")

    def get_email(self) -> Optional[str]:
        """Get user's email."""
        return self._get_user_data().get("email")

    def is_email_verified(self) -> bool:
        """Check if user's email is verified."""
        return self._get_user_data().get("is_email_verified", False)

    def get_email_verification_status(self) -> Dict:
        """Get email verification status."""
        data = self._get_user_data()
        return {
            "email": data.get("email"),
            "is_verified": data.get("is_email_verified", False),
            "verified_at": data.get("email_verified_at"),
        }

    def get_session_summary(self) -> Dict:
        """Get summary of user's data."""
        data = self._get_user_data()
        return {
            "user_id": data["user_id"],
            "browser_id": self.browser_id[:8],
            "analyses_performed": data["analyses_count"],
            "comparisons_performed": data["comparisons_count"],
            "is_paid": data["is_paid_user"],
            "total_spent": sum(p["amount"] for p in data["payment_history"]),
            "created_at": data["created_at"],
            "last_accessed": data["last_accessed"],
        }

    # =========================================================================
    # DEBUG & TESTING UTILITIES
    # =========================================================================

    def reset_user_data(self, keep_user_id: bool = False):
        """
        Reset all user data (for testing/debugging).

        Args:
            keep_user_id: If True, preserve user_id; otherwise generate new one
        """
        try:
            old_id = self._get_user_data()["user_id"]

            new_data = {
                "version": self.DATA_VERSION,
                "user_id": old_id if keep_user_id else self._generate_persistent_user_id(),
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "analyses_count": 0,
                "comparisons_count": 0,
                "is_paid_user": False,
                "payment_history": [],
            }

            self.storage.set_item(self.browser_id, "user_data", new_data)
            st.session_state._persistent_user_data = new_data

            logger.warning(f"User data reset (keep_user_id={keep_user_id})")
            return True
        except Exception as e:
            logger.error(f"Error resetting user data: {e}")
            return False

    def clear_all_storage(self):
        """Clear all stored data for this browser (for testing)."""
        try:
            self.storage.clear_all_for_browser(self.browser_id)
            logger.warning(f"Cleared all storage for browser {self.browser_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
            return False

    def get_debug_info(self) -> Dict:
        """Get comprehensive debug information."""
        return {
            "browser_id": self.browser_id,
            "user_id": self.get_user_id(),
            "user_data": self._get_user_data(),
            "storage_location": "hybrid (session + filesystem)",
            "is_streamlit_cloud": is_streamlit_cloud(),
            "session_state_keys": list(st.session_state.keys()),
        }

    def export_user_data(self) -> str:
        """Export user data as JSON string (for backup/debugging)."""
        try:
            data = self._get_user_data()
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return "{}"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Cloud."""
    try:
        return "streamlit.app" in st.config.get_option("server.baseUrlPath")
    except Exception:
        return False


def show_persistent_debug_panel():
    """Debug panel for development - shows storage state."""
    with st.expander("🔧 Storage Debug Panel"):
        user_manager = PersistentUserManager()
        debug_info = user_manager.get_debug_info()

        col1, col2 = st.columns(2)

        with col1:
            st.write("**User Info:**")
            st.code(f"User ID: {user_manager.get_user_id()}\n"
                   f"Browser ID: {user_manager.get_browser_id()[:8]}...")

            st.write("**Storage Type:**")
            st.info(f"Location: {debug_info['storage_location']}\n"
                   f"Cloud: {debug_info['is_streamlit_cloud']}")

        with col2:
            st.write("**Data Summary:**")
            st.json(user_manager.get_session_summary())

        st.write("**Full Debug Info:**")
        st.json(debug_info)

        st.write("**Raw User Data:**")
        st.code(user_manager.export_user_data())

        # Actions
        st.subheader("Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Reset User Data"):
                user_manager.reset_user_data()
                st.success("Reset complete")
                st.rerun()

        with col2:
            if st.button("🗑️ Clear All Storage"):
                user_manager.clear_all_storage()
                st.success("Storage cleared")
                st.rerun()

        with col3:
            if st.button("📋 Copy JSON"):
                st.code(user_manager.export_user_data())
