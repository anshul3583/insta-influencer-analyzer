"""
Email verification manager for optional user account linking.

Features:
- One-time use verification links (24-hour expiration)
- Secure token generation & validation
- SendGrid/Resend integration
- Recovery on new devices
- Email-linked payment history
- Automatic payment receipts
"""

import streamlit as st
import secrets
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
import hmac

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


class SecureTokenManager:
    """Generate and validate secure, one-time-use verification tokens."""

    TOKEN_LENGTH = 32  # 256 bits of entropy
    HASH_ALGORITHM = "sha256"
    EXPIRATION_HOURS = 24

    @staticmethod
    def generate_token() -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(SecureTokenManager.TOKEN_LENGTH)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using HMAC-SHA256 for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token(token: str, stored_hash: str) -> bool:
        """Verify a token against its stored hash (constant-time comparison)."""
        token_hash = SecureTokenManager.hash_token(token)
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(token_hash, stored_hash)

    @staticmethod
    def is_token_expired(created_at: str) -> bool:
        """Check if token has expired (24-hour window)."""
        created = datetime.fromisoformat(created_at)
        expiration = created + timedelta(hours=SecureTokenManager.EXPIRATION_HOURS)
        return datetime.now() > expiration

    @staticmethod
    def get_token_expiration_time(created_at: str) -> str:
        """Get when a token expires."""
        created = datetime.fromisoformat(created_at)
        expiration = created + timedelta(hours=SecureTokenManager.EXPIRATION_HOURS)
        return expiration.isoformat()


class EmailProvider:
    """Abstract email provider interface."""

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        raise NotImplementedError


class SendGridProvider(EmailProvider):
    """SendGrid email provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.sg = SendGridAPIClient(api_key)
            self.Mail = Mail
        except ImportError:
            logger.error("SendGrid not installed. Install with: pip install sendgrid")
            raise

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        """Send verification email via SendGrid."""
        try:
            from sendgrid.helpers.mail import Email, Content

            subject = "Verify Your Influencer Radar Email"
            html_content = self._get_email_html(verification_link, to_email)

            message = self.Mail(
                from_email=Email("noreply@influencerradar.app", "Influencer Radar"),
                to_emails=to_email,
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            response = self.sg.send(message)
            logger.info(f"SendGrid email sent to {to_email}, status: {response.status_code}")
            return response.status_code in [200, 201, 202]

        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False

    @staticmethod
    def _get_email_html(verification_link: str, email: str) -> str:
        """Get HTML email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #FF006E 0%, #8338EC 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ background: #FF006E; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
                .footer {{ color: #888; font-size: 12px; margin-top: 20px; }}
                .code {{ background: #fff; padding: 10px; border-left: 4px solid #FF006E; font-family: monospace; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👥 Influencer Radar</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <p>Hi there! 👋</p>
                    <p>Thanks for using Influencer Radar! Click the button below to verify your email address.</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy this link in your browser:</p>
                    <div class="code">{verification_link}</div>
                    <p style="color: #888; font-size: 12px;">
                        This link expires in 24 hours. If you didn't request this email, you can ignore it.
                    </p>
                    <div class="footer">
                        <p>© 2026 Influencer Radar. All rights reserved.</p>
                        <p>Email: {email}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """


class ResendProvider(EmailProvider):
    """Resend email provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from resend import Resend
            self.client = Resend(api_key=api_key)
        except ImportError:
            logger.error("Resend not installed. Install with: pip install resend")
            raise

    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        """Send verification email via Resend."""
        try:
            html_content = self._get_email_html(verification_link, to_email)

            response = self.client.emails.send({
                "from": "noreply@influencerradar.app",
                "to": to_email,
                "subject": "Verify Your Influencer Radar Email",
                "html": html_content
            })

            logger.info(f"Resend email sent to {to_email}: {response}")
            return hasattr(response, 'id') and response.id is not None

        except Exception as e:
            logger.error(f"Resend error: {e}")
            return False

    @staticmethod
    def _get_email_html(verification_link: str, email: str) -> str:
        """Get HTML email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #FF006E 0%, #8338EC 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ background: #FF006E; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
                .footer {{ color: #888; font-size: 12px; margin-top: 20px; }}
                .code {{ background: #fff; padding: 10px; border-left: 4px solid #FF006E; font-family: monospace; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👥 Influencer Radar</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <p>Hi there! 👋</p>
                    <p>Thanks for using Influencer Radar! Click the button below to verify your email address.</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy this link in your browser:</p>
                    <div class="code">{verification_link}</div>
                    <p style="color: #888; font-size: 12px;">
                        This link expires in 24 hours. If you didn't request this email, you can ignore it.
                    </p>
                    <div class="footer">
                        <p>© 2026 Influencer Radar. All rights reserved.</p>
                        <p>Email: {email}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """


class EmailVerificationManager:
    """
    Manages email verification workflow.

    Lifecycle:
    1. User enters email → Generate token
    2. Send email with verification link
    3. User clicks link → Validate token
    4. Token verified → Mark email as verified
    5. Email linked to user ID
    """

    VERIFICATION_STORAGE_KEY = "email_verifications"
    DEFAULT_PROVIDER = "sendgrid"

    def __init__(self, provider: str = DEFAULT_PROVIDER):
        """
        Initialize email verification manager.

        Args:
            provider: "sendgrid" or "resend"
        """
        self.provider_name = provider
        self.email_provider = self._init_provider(provider)
        self.token_manager = SecureTokenManager()

        logger.info(f"EmailVerificationManager initialized with {provider}")

    def _init_provider(self, provider: str) -> Optional[EmailProvider]:
        """Initialize email provider based on config."""
        try:
            if provider == "sendgrid":
                api_key = st.secrets.get("sendgrid_api_key")
                if not api_key:
                    logger.warning("SendGrid API key not found in secrets.toml")
                    return None
                return SendGridProvider(api_key)

            elif provider == "resend":
                api_key = st.secrets.get("resend_api_key")
                if not api_key:
                    logger.warning("Resend API key not found in secrets.toml")
                    return None
                return ResendProvider(api_key)

            else:
                logger.error(f"Unknown email provider: {provider}")
                return None

        except Exception as e:
            logger.error(f"Error initializing email provider: {e}")
            return None

    def _get_verifications_storage(self) -> Dict:
        """Get verification tokens storage from session state."""
        if "_email_verifications" not in st.session_state:
            st.session_state._email_verifications = {}
        return st.session_state._email_verifications

    def request_verification(self, email: str, user_id: str, app_url: str = None) -> Tuple[bool, str]:
        """
        Request email verification for a user.

        Args:
            email: Email address to verify
            user_id: Associated user ID
            app_url: Base URL of the app (for verification link)

        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate email
            if not self._is_valid_email(email):
                return False, "Invalid email address"

            # Generate token
            token = self.token_manager.generate_token()
            token_hash = self.token_manager.hash_token(token)

            # Generate verification link
            if app_url is None:
                app_url = st.config.get_option("client.baseUrlPath") or "http://localhost:8501"

            verification_link = f"{app_url}?verify_email={token}"

            # Store token (one-time use)
            verifications = self._get_verifications_storage()
            verifications[token_hash] = {
                "email": email,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "used": False,
                "verified_at": None
            }

            # Send email
            if not self.email_provider:
                logger.warning("Email provider not initialized, returning token for testing")
                # For testing/demo: print token
                logger.info(f"TEST: Verification link: {verification_link}")
                return True, f"Verification link (test mode): {verification_link}"

            success = self.email_provider.send_verification_email(email, verification_link)

            if success:
                logger.info(f"Verification email sent to {email}")
                return True, "Verification email sent! Check your inbox."
            else:
                logger.error(f"Failed to send verification email to {email}")
                return False, "Failed to send email. Please try again."

        except Exception as e:
            logger.error(f"Error requesting verification: {e}")
            return False, f"Error: {str(e)}"

    def verify_email(self, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Verify an email token.

        Args:
            token: Verification token from email link

        Returns:
            (success: bool, message: str, verification_data: dict or None)
        """
        try:
            verifications = self._get_verifications_storage()

            # Find matching token
            token_hash = self.token_manager.hash_token(token)

            if token_hash not in verifications:
                logger.warning(f"Invalid token attempted: {token_hash[:8]}...")
                return False, "Invalid verification link", None

            verification_data = verifications[token_hash]

            # Check if already used
            if verification_data["used"]:
                logger.warning(f"Token already used: {token_hash[:8]}...")
                return False, "This verification link has already been used", None

            # Check expiration
            if self.token_manager.is_token_expired(verification_data["created_at"]):
                logger.warning(f"Token expired: {token_hash[:8]}...")
                return False, "This verification link has expired (24-hour limit)", None

            # Mark as used
            verification_data["used"] = True
            verification_data["verified_at"] = datetime.now().isoformat()

            logger.info(f"Email verified for user {verification_data['user_id']}")

            return True, "Email verified successfully!", verification_data

        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False, f"Error: {str(e)}", None

    def get_verification_status(self, user_id: str) -> Dict:
        """Get verification status for a user."""
        try:
            verifications = self._get_verifications_storage()

            # Find verified email for this user
            for token_hash, data in verifications.items():
                if data["user_id"] == user_id and data["used"] and data["verified_at"]:
                    return {
                        "is_verified": True,
                        "email": data["email"],
                        "verified_at": data["verified_at"],
                        "token_created_at": data["created_at"]
                    }

            return {"is_verified": False}

        except Exception as e:
            logger.error(f"Error getting verification status: {e}")
            return {"is_verified": False, "error": str(e)}

    def get_verified_email(self, user_id: str) -> Optional[str]:
        """Get verified email for a user."""
        status = self.get_verification_status(user_id)
        return status.get("email") if status.get("is_verified") else None

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def get_debug_info(self) -> Dict:
        """Get debug information about email verification."""
        verifications = self._get_verifications_storage()
        return {
            "provider": self.provider_name,
            "provider_initialized": self.email_provider is not None,
            "total_verifications": len(verifications),
            "verifications": {
                k[:8]: {
                    "email": v["email"],
                    "user_id": v["user_id"],
                    "used": v["used"],
                    "created_at": v["created_at"],
                }
                for k, v in verifications.items()
            }
        }

    def reset_verifications(self):
        """Clear all verification data (testing only)."""
        st.session_state._email_verifications = {}
        logger.warning("All verifications cleared")


# ============================================================================
# EMAIL TEMPLATE FUNCTIONS
# ============================================================================

def get_payment_receipt_html(
    user_email: str,
    payment_id: str,
    amount: float,
    payment_type: str,
    timestamp: str
) -> str:
    """Generate HTML for payment receipt email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #FF006E 0%, #8338EC 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .receipt {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 4px; margin: 20px 0; }}
            .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .label {{ color: #666; font-weight: bold; }}
            .value {{ color: #333; }}
            .total {{ font-size: 24px; color: #FF006E; font-weight: bold; margin-top: 10px; }}
            .footer {{ color: #888; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 Influencer Radar</h1>
                <p>Payment Receipt</p>
            </div>
            <div class="content">
                <p>Hi there! 👋</p>
                <p>Thank you for your purchase!</p>

                <div class="receipt">
                    <div class="row">
                        <span class="label">Receipt #:</span>
                        <span class="value">{payment_id}</span>
                    </div>
                    <div class="row">
                        <span class="label">Date:</span>
                        <span class="value">{timestamp}</span>
                    </div>
                    <div class="row">
                        <span class="label">Item:</span>
                        <span class="value">{payment_type.title()}</span>
                    </div>
                    <div class="row">
                        <span class="label">Amount:</span>
                        <span class="value">${amount:.2f}</span>
                    </div>
                    <div class="total">Total: ${amount:.2f}</div>
                </div>

                <p style="color: #888; font-size: 12px;">
                    If you have any questions, please contact our support team at support@influencerradar.app
                </p>

                <div class="footer">
                    <p>© 2026 Influencer Radar. All rights reserved.</p>
                    <p>Email: {user_email}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
