"""
Email verification UI components for Streamlit app.

Provides ready-to-use components for:
- Email input form
- Verification status badge
- Verification link handler
- Recovery flow
"""

import streamlit as st
from modules.email_manager import EmailVerificationManager
from typing import Optional, Callable


def show_email_verification_widget(
    user_manager,
    email_manager: EmailVerificationManager,
    app_url: str = None
):
    """
    Display email verification widget in sidebar.

    Shows email input, send verification, and verification status.
    """
    st.markdown("---")
    st.markdown("### 📧 Email Verification")

    # Get verification status
    user_id = user_manager.get_user_id()
    verification_status = email_manager.get_verification_status(user_id)

    if verification_status.get("is_verified"):
        # Already verified
        email = verification_status.get("email")
        st.success(f"✅ **Verified:** {email}")

        if st.button("🔗 Change Email", key="change_email"):
            st.session_state.show_email_form = True

    else:
        # Not verified yet
        st.info("🔓 Optionally verify your email to recover account on new devices")

        if st.session_state.get("show_email_form"):
            with st.form("email_verification_form"):
                email = st.text_input(
                    "Enter your email",
                    placeholder="you@example.com",
                    key="email_input"
                )

                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("📧 Send Verification")
                with col2:
                    cancel = st.form_submit_button("Cancel")

                if cancel:
                    st.session_state.show_email_form = False
                    st.rerun()

                if submit and email:
                    with st.spinner("Sending verification email..."):
                        success, message = email_manager.request_verification(
                            email,
                            user_id,
                            app_url
                        )

                        if success:
                            st.success(message)
                            st.session_state.show_email_form = False
                            st.session_state.verification_email_sent = email
                            logger.info(f"Verification email sent to {email}")
                        else:
                            st.error(message)

        else:
            if st.button("📧 Verify Email", use_container_width=True):
                st.session_state.show_email_form = True
                st.rerun()

    st.markdown("---")


def show_verification_status_badge(email_manager: EmailVerificationManager, user_id: str):
    """Show verification status badge for display."""
    status = email_manager.get_verification_status(user_id)

    if status.get("is_verified"):
        st.markdown(
            '<div style="background-color: #00D084; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block;">✅ EMAIL VERIFIED</div>',
            unsafe_allow_html=True
        )
        return f"Verified: {status.get('email')}"
    else:
        st.markdown(
            '<div style="background-color: #FFA500; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block;">⏳ UNVERIFIED</div>',
            unsafe_allow_html=True
        )
        return "Email not verified"


def handle_verification_link(email_manager: EmailVerificationManager, user_manager):
    """
    Handle email verification link from URL parameter.

    Call this in app.py at startup to check for verify_email query param.
    """
    import streamlit as st

    query_params = st.query_params

    if "verify_email" in query_params:
        token = query_params.get("verify_email", "")

        if token:
            with st.spinner("Verifying email..."):
                success, message, verification_data = email_manager.verify_email(token)

                if success:
                    # Link email to user
                    user_manager.set_verified_email(
                        verification_data["email"]
                    )

                    # Clear query param
                    query_params.clear()

                    st.success(
                        f"🎉 **Email Verified!**\n\n"
                        f"Your email **{verification_data['email']}** is now verified.\n\n"
                        f"You can now:\n"
                        f"- Recover your account from any device\n"
                        f"- Receive payment receipts automatically\n"
                        f"- Access payment history with login"
                    )

                    logger.info(f"Email verified for user {verification_data['user_id']}")

                else:
                    st.error(f"❌ **Verification Failed**\n\n{message}")
                    logger.warning(f"Email verification failed: {message}")

                # Stop execution to show result
                st.stop()


def show_payment_receipt_prompt(
    email_manager: EmailVerificationManager,
    user_manager,
    payment_id: str,
    amount: float,
    payment_type: str
):
    """
    Show prompt to send payment receipt to verified email.

    Call after successful payment.
    """
    verified_email = email_manager.get_verified_email(user_manager.get_user_id())

    if verified_email:
        st.info(f"💳 Receipt will be sent to {verified_email}")
        # In real implementation, send receipt email here
    else:
        st.info(
            "💡 Verify your email to automatically receive payment receipts"
        )


def show_recovery_flow(
    email_manager: EmailVerificationManager,
    user_manager
):
    """
    Show account recovery flow.

    Allows users on new devices to link their account via verified email.
    """
    st.markdown("### 🔐 Recover Your Account")

    with st.form("recovery_form"):
        st.write("If you're using a new device, recover your account with your verified email:")

        email = st.text_input(
            "Enter your verified email",
            placeholder="you@example.com"
        )

        submitted = st.form_submit_button("🔓 Send Recovery Link")

        if submitted and email:
            verified_email = email_manager.get_verified_email(user_manager.get_user_id())

            if verified_email == email:
                st.success("Recovery link sent to your email!")
                # In real implementation: generate recovery link
            else:
                st.error("Email not verified or doesn't match records")


def show_email_debug_panel(email_manager: EmailVerificationManager):
    """Debug panel for email verification (development only)."""
    with st.expander("🔧 Email Debug Panel"):
        debug_info = email_manager.get_debug_info()

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Provider Info:**")
            st.code(f"""
Provider: {debug_info['provider']}
Initialized: {debug_info['provider_initialized']}
Total Verifications: {debug_info['total_verifications']}
            """)

        with col2:
            st.write("**Verifications:**")
            if debug_info['verifications']:
                for token_prefix, data in debug_info['verifications'].items():
                    st.write(f"""
**Token: {token_prefix}...**
- Email: {data['email']}
- User: {data['user_id']}
- Used: {data['used']}
- Created: {data['created_at'][:10]}
                    """)

        # Test email send
        st.subheader("Test Email Send")

        test_email = st.text_input("Test email address", placeholder="test@example.com")

        if st.button("📧 Send Test Email"):
            if email_manager.email_provider:
                link = "http://localhost:8501?verify_email=test_token_123"
                success = email_manager.email_provider.send_verification_email(
                    test_email,
                    link
                )
                if success:
                    st.success(f"Test email sent to {test_email}")
                else:
                    st.error("Failed to send test email")
            else:
                st.error("Email provider not initialized")

        # Clear data
        if st.button("🗑️ Clear All Verifications"):
            email_manager.reset_verifications()
            st.success("Cleared all verification data")
            st.rerun()


# Import for logging
import logging
logger = logging.getLogger(__name__)
