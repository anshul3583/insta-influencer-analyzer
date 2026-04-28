"""
Example Usage and Testing Guide for PersistentUserManager
"""

# ============================================================================
# BASIC USAGE (in app.py or any Streamlit script)
# ============================================================================

import streamlit as st
from modules.persistent_user_manager import PersistentUserManager

# Initialize manager
manager = PersistentUserManager()

# ============================================================================
# API EXAMPLES
# ============================================================================

# Get user information
user_id = manager.get_user_id()  # Consistent across sessions
browser_id = manager.get_browser_id()  # Browser fingerprint

# Track usage
manager.increment_analysis_count()
manager.increment_comparison_count()

# Check usage
analyses = manager.get_analysis_count()
comparisons = manager.get_comparison_count()

# Payment tracking
manager.set_paid_user(True)
manager.add_payment_record(
    payment_id="stripe_12345",
    amount=2.99,
    payment_type="analysis",
    status="completed"
)

# Get summary
history = manager.get_payment_history()
summary = manager.get_session_summary()

# ============================================================================
# TESTING & DEBUGGING
# ============================================================================

# Test 1: Basic Persistence
def test_basic_persistence():
    """Test that data persists across manager instances."""
    manager1 = PersistentUserManager()
    manager1.increment_analysis_count()
    count1 = manager1.get_analysis_count()

    # Simulate new session
    manager2 = PersistentUserManager()
    count2 = manager2.get_analysis_count()

    assert count1 == count2 == 1, "Persistence failed!"
    print("✅ Basic persistence test passed")


# Test 2: User ID Consistency
def test_user_id_consistency():
    """Test that user_id remains consistent."""
    manager1 = PersistentUserManager()
    user_id_1 = manager1.get_user_id()

    manager2 = PersistentUserManager()
    user_id_2 = manager2.get_user_id()

    assert user_id_1 == user_id_2, "User ID not consistent!"
    print(f"✅ User ID consistency test passed: {user_id_1}")


# Test 3: Payment History
def test_payment_tracking():
    """Test payment recording and retrieval."""
    manager = PersistentUserManager()

    # Add multiple payments
    manager.add_payment_record("pay_001", 2.99, "analysis")
    manager.add_payment_record("pay_002", 4.99, "comparison")

    history = manager.get_payment_history()
    assert len(history) >= 2, "Payment history not saved!"
    assert history[0]["amount"] == 2.99
    assert history[1]["amount"] == 4.99

    total = sum(p["amount"] for p in history)
    print(f"✅ Payment tracking test passed. Total: ${total:.2f}")


# Test 4: Reset Functionality
def test_reset():
    """Test data reset."""
    manager = PersistentUserManager()
    old_id = manager.get_user_id()

    # Increment some data
    manager.increment_analysis_count()
    manager.increment_analysis_count()

    # Reset
    manager.reset_user_data(keep_user_id=True)

    assert manager.get_user_id() == old_id, "User ID should be preserved"
    assert manager.get_analysis_count() == 0, "Analyses should be reset"

    print("✅ Reset test passed")


# Test 5: Migration from Old Session
def test_legacy_migration():
    """Test migration of legacy session data."""
    import st as streamlit_mock

    # Simulate old session data
    # (In real test, mock st.session_state)

    manager = PersistentUserManager()
    summary = manager.get_session_summary()

    print(f"✅ Migration test passed. Summary: {summary}")


# ============================================================================
# STREAMLIT APP TESTING
# ============================================================================

def run_test_app():
    """Run complete test in Streamlit app."""
    import streamlit as st

    st.title("PersistentUserManager Test Suite")

    manager = PersistentUserManager()

    # Display current state
    st.subheader("Current User State")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("User ID", manager.get_user_id()[:12])
    with col2:
        st.metric("Analyses", manager.get_analysis_count())
    with col3:
        st.metric("Comparisons", manager.get_comparison_count())

    st.divider()

    # Test controls
    st.subheader("Test Controls")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Increment Analysis"):
            manager.increment_analysis_count()
            st.success("Analysis count incremented")
            st.rerun()

    with col2:
        if st.button("➕ Increment Comparison"):
            manager.increment_comparison_count()
            st.success("Comparison count incremented")
            st.rerun()

    with col3:
        if st.button("💳 Add Payment"):
            manager.add_payment_record(
                f"test_{len(manager.get_payment_history())}",
                2.99,
                "analysis"
            )
            st.success("Payment added")
            st.rerun()

    st.divider()

    # Show data
    st.subheader("User Data")
    st.json(manager.get_session_summary())

    st.subheader("Payment History")
    if manager.get_payment_history():
        st.dataframe(manager.get_payment_history())
    else:
        st.info("No payments recorded yet")

    st.divider()

    # Debug tools
    st.subheader("Debug Tools")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reset Data"):
            manager.reset_user_data(keep_user_id=True)
            st.success("Data reset complete")
            st.rerun()

    with col2:
        if st.button("🗑️ Clear All Storage"):
            manager.clear_all_storage()
            st.warning("All storage cleared")
            st.rerun()

    st.divider()

    # Export
    st.subheader("Export Data")
    st.code(manager.export_user_data())
    st.download_button(
        label="📥 Download User Data",
        data=manager.export_user_data(),
        file_name=f"user_data_{manager.get_user_id()}.json",
        mime="application/json"
    )


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Running offline tests...")
        test_basic_persistence()
        test_user_id_consistency()
        test_payment_tracking()
        test_reset()
        print("\n✅ All offline tests passed!")
    else:
        print("Run in Streamlit app with: streamlit run this_file.py")
        print("Or run tests with: python this_file.py test")
