"""Stripe payment processing and management."""
import streamlit as st
import stripe
from typing import Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StripeHandler:
    """Handles all Stripe payment operations for the SaaS app."""

    # Pricing configuration (in cents USD)
    ANALYSIS_PRICE = 299      # $2.99
    COMPARISON_PRICE = 499    # $4.99

    def __init__(self):
        """Initialize Stripe with API key."""
        self.secret_key = st.secrets.get("STRIPE_SECRET_KEY")
        self.public_key = st.secrets.get("STRIPE_PUBLIC_KEY")

        if not self.secret_key:
            raise ValueError(
                "❌ STRIPE_SECRET_KEY not configured in .streamlit/secrets.toml")

        stripe.api_key = self.secret_key
        logger.info("✅ Stripe handler initialized")

    def create_checkout_session(
        self,
        user_id: str,
        analysis_type: str = "analysis"
    ) -> Dict:
        """
        Create a Stripe Checkout session.

        Args:
            user_id: Unique user identifier
            analysis_type: "analysis" or "comparison"

        Returns:
            Dict with session_id, checkout_url, and success status
        """
        try:
            # Determine price and product details
            if analysis_type == "comparison":
                price = self.COMPARISON_PRICE
                product_name = "🔄 Influencer Comparison"
                description = "Side-by-side comparison of 2 influencers with GPT-4 insights"
            else:
                price = self.ANALYSIS_PRICE
                product_name = "📊 Single Influencer Analysis"
                description = "Deep analysis of 1 influencer with metrics & sponsorship value"

            # Get redirect URLs from secrets
            base_url = st.secrets.get("SUCCESS_URL", "http://localhost:8501")

            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": price,
                            "product_data": {
                                "name": product_name,
                                "description": description,
                                "images": [],
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{base_url}?success={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{base_url}?canceled=true",
                client_reference_id=user_id,
                metadata={
                    "user_id": user_id,
                    "analysis_type": analysis_type,
                }
            )

            logger.info(f"✅ Checkout session created: {checkout_session.id}")

            return {
                "session_id": checkout_session.id,
                "checkout_url": checkout_session.url,
                "success": True
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def verify_payment(self, session_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify if a payment was successful.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Tuple of (success: bool, payment_details: dict or None)
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                payment_details = {
                    "session_id": session_id,
                    "amount": session.amount_total / 100,  # Convert cents to dollars
                    "currency": session.currency.upper(),
                    "status": session.payment_status,
                    "user_id": session.client_reference_id,
                    "analysis_type": session.metadata.get("analysis_type"),
                    "payment_intent_id": session.payment_intent,
                    "created_at": session.created
                }
                logger.info(f"✅ Payment verified: {session_id}")
                return True, payment_details

            logger.info(
                f"⏳ Payment not yet completed for session: {session_id}")
            return False, None

        except stripe.error.StripeError as e:
            logger.error(f"❌ Error verifying payment: {str(e)}")
            return False, None

    def get_checkout_url(self, session_id: str) -> Optional[str]:
        """Retrieve checkout URL from existing session."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving session: {str(e)}")
            return None

    def refund_payment(self, payment_intent_id: str,
                       reason: str = "requested_by_customer") -> Tuple[bool, Optional[str]]:
        """
        Refund a payment (for admin use).

        Args:
            payment_intent_id: Stripe payment intent ID
            reason: Reason for refund

        Returns:
            Tuple of (success: bool, refund_id: str or error_message: str)
        """
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                reason=reason
            )
            logger.info(f"✅ Refund created: {refund.id}")
            return True, refund.id

        except stripe.error.StripeError as e:
            logger.error(f"❌ Refund error: {str(e)}")
            return False, str(e)


def get_stripe_handler() -> StripeHandler:
    """Get or create a Stripe handler instance (singleton)."""
    if "stripe_handler" not in st.session_state:
        try:
            st.session_state.stripe_handler = StripeHandler()
        except ValueError as e:
            st.error(f"⚠️ {str(e)}")
            st.stop()

    return st.session_state.stripe_handler
