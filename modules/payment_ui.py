"""Payment UI components and flows."""
import streamlit as st
from modules.stripe_handler import get_stripe_handler
from modules.user_manager import UserManager


def show_payment_prompt(analysis_type: str = "analysis"):
    """
    Display payment prompt when user tries to perform a paid action.

    Args:
        analysis_type: "analysis" or "comparison"
    """
    user_manager = UserManager()
    stripe_handler = get_stripe_handler()

    if analysis_type == "comparison":
        price = "$4.99"
        emoji = "🔄"
        title = "Comparison Unlocked"
        description = "Compare two influencers side-by-side with AI-powered insights"
    else:
        price = "$2.99"
        emoji = "📊"
        title = "Additional Analysis"
        description = "Analyze another influencer with detailed metrics"

    st.warning(
        f"### {emoji} {title}\nYour first analysis is free! This {analysis_type} costs **{price}**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💳 Pay {price}", key=f"pay_{analysis_type}", use_container_width=True):
            checkout_result = stripe_handler.create_checkout_session(
                user_id=user_manager.get_user_id(),
                analysis_type=analysis_type
            )

            if checkout_result["success"]:
                # Store session ID for verification
                user_manager.set_last_payment_session(
                    checkout_result["session_id"])

                st.session_state[f"{analysis_type}_checkout_url"] = checkout_result["checkout_url"]
                st.info("✅ Redirecting to checkout...")
                st.markdown(
                    f"[Click here if not redirected]({checkout_result['checkout_url']})")
                st.stop()
            else:
                st.error(f"❌ Payment error: {checkout_result.get('error')}")

    with col2:
        st.button(
            "❌ Cancel", key=f"cancel_{analysis_type}", use_container_width=True)


def check_and_handle_payment_redirect():
    """Check URL parameters for successful/cancelled payments."""
    from urllib.parse import parse_qs

    user_manager = UserManager()
    stripe_handler = get_stripe_handler()

    query_params = st.query_params

    # Handle successful payment
    if "success" in query_params:
        session_id = query_params.get("success", [None])[0] if isinstance(
            query_params.get("success"), list) else query_params.get("success")

        if session_id:
            success, payment_details = stripe_handler.verify_payment(
                session_id)

            if success:
                # Mark user as paid
                user_manager.set_paid_user(True)
                user_manager.add_payment_record(
                    payment_id=payment_details["payment_intent_id"],
                    amount=payment_details["amount"],
                    payment_type=payment_details["analysis_type"],
                    status="completed"
                )

                st.success(f"""
                ### ✅ Payment Successful!
                **Amount:** ${payment_details['amount']}  
                **Type:** {payment_details['analysis_type'].title()}  
                **Transaction ID:** `{session_id[:20]}...`
                
                You can now perform unlimited analyses and comparisons! 🎉
                """)

                # Clear the URL parameter
                st.query_params.clear()
                st.rerun()

    # Handle cancelled payment
    if query_params.get("canceled") == "true":
        st.warning("❌ Payment cancelled. No charges were made.")
        st.query_params.clear()


def show_payment_history():
    """Display user's payment history in a table."""
    user_manager = UserManager()
