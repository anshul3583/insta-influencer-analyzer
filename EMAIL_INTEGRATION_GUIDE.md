# Email Verification Integration Guide

## Overview

This guide walks you through integrating optional email verification into your Streamlit app. Users can optionally verify their email to enable account recovery and automatic payment receipts.

---

## 1. Setup: Choose Email Provider

### Option A: SendGrid (Recommended)

**Installation:**

```bash
pip install sendgrid
```

**Get API Key:**

1. Sign up at https://sendgrid.com
2. Create API key in Settings → API Keys
3. Add to `secrets.toml`:

```toml
# .streamlit/secrets.toml
sendgrid_api_key = "SG.your_api_key_here"
email_provider = "sendgrid"
```

### Option B: Resend

**Installation:**

```bash
pip install resend
```

**Get API Key:**

1. Sign up at https://resend.com
2. Create API key in Tokens section
3. Add to `secrets.toml`:

```toml
# .streamlit/secrets.toml
resend_api_key = "re_your_api_key_here"
email_provider = "resend"
```

---

## 2. Code Changes in app.py

### Step 1: Add Imports (Top of file)

```python
from modules.persistent_user_manager import PersistentUserManager
from modules.email_manager import EmailVerificationManager
from modules.email_ui import (
    show_email_verification_widget,
    handle_verification_link,
    show_email_debug_panel,
)
```

### Step 2: Initialize Manager (In INITIALIZATION section)

```python
# After user_manager initialization
try:
    email_manager = EmailVerificationManager(
        provider=st.secrets.get("email_provider", "sendgrid")
    )
except Exception as e:
    st.warning(f"Email verification unavailable: {str(e)}")
    email_manager = None
```

### Step 3: Handle Verification Links (After page config, before sidebar)

```python
# Check if user clicked verification link
if email_manager:
    handle_verification_link(email_manager, user_manager)
```

### Step 4: Add Widget to Sidebar (In sidebar section, after debug info)

```python
with st.sidebar:
    # ... existing sidebar code ...

    # Email verification widget
    if email_manager:
        show_email_verification_widget(
            user_manager,
            email_manager,
            app_url="https://your-app-url.com"  # Change for production
        )

    # Email debug panel (remove for production)
    if st.checkbox("🔧 Email Debug"):
        show_email_debug_panel(email_manager)
```

---

## 3. Full Integration Example

```python
"""
Instagram Influencer Analyzer - With Email Verification
"""

import streamlit as st
from modules.stripe_handler import get_stripe_handler
from modules.persistent_user_manager import PersistentUserManager
from modules.email_manager import EmailVerificationManager
from modules.payment_ui import show_payment_prompt, check_and_handle_payment_redirect
from modules.email_ui import (
    show_email_verification_widget,
    handle_verification_link,
    show_email_debug_panel,
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="👥 Influencer Radar",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INITIALIZATION
# ============================================================================

user_manager = PersistentUserManager()

try:
    stripe_handler = get_stripe_handler()
except Exception as e:
    st.error(f"⚠️ Payment system error: {str(e)}")
    st.stop()

# Initialize email manager
try:
    email_manager = EmailVerificationManager(
        provider=st.secrets.get("email_provider", "sendgrid")
    )
except Exception as e:
    st.warning(f"Email verification unavailable: {str(e)}")
    email_manager = None

# ============================================================================
# HANDLE VERIFICATION LINKS
# ============================================================================

if email_manager:
    handle_verification_link(email_manager, user_manager)

check_and_handle_payment_redirect()

# ============================================================================
# SIDEBAR - USER INFO & EMAIL VERIFICATION
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Your Session")

    user_id = user_manager.get_user_id()
    st.caption(f"**User ID:** `{user_id[:8]}...`")

    # Payment status
    if user_manager.is_paid():
        st.markdown(
            '<div class="payment-badge">✅ PREMIUM MEMBER</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="free-badge">🆓 FREE TIER (1 free analysis)</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Usage statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Analyses Used",
            value=user_manager.get_analysis_count(),
            delta="1 free"
        )
    with col2:
        st.metric(
            label="Comparisons",
            value=user_manager.get_comparison_count()
        )

    st.markdown("---")

    # Payment history
    if user_manager.get_payment_history():
        with st.expander("💳 Payment History"):
            for payment in user_manager.get_payment_history():
                st.write(f"""
                **${payment['amount']}** - {payment['type'].title()}
                {payment['timestamp'][:10]}
                Status: {payment['status']}
                """)

    st.markdown("---")

    # Email verification widget
    if email_manager:
        show_email_verification_widget(
            user_manager,
            email_manager,
            app_url=st.config.get_option("client.baseUrlPath")
        )

    st.markdown("---")

    # Debug info
    if st.checkbox("🔍 Debug Info"):
        st.code(f"""
User ID: {user_id}
Browser ID: {user_manager.get_browser_id()[:8]}...
Analyses: {user_manager.get_analysis_count()}
Email Verified: {user_manager.is_email_verified()}
Storage: ✅ Persistent
        """)

    # Email debug (remove for production)
    if st.checkbox("🔧 Email Debug"):
        if email_manager:
            show_email_debug_panel(email_manager)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("👥 Influencer Radar")
st.markdown("*Deep dive into any influencer • Compare like a pro • Get the tea ☕*")
st.markdown("---")

# ... rest of your app ...
```

---

## 4. Sending Payment Receipts to Verified Email

### After Payment Processing

```python
if user_manager.is_email_verified():
    verified_email = user_manager.get_email()

    # Send receipt email
    from modules.email_manager import get_payment_receipt_html

    receipt_html = get_payment_receipt_html(
        user_email=verified_email,
        payment_id=stripe_payment_id,
        amount=amount,
        payment_type="analysis",
        timestamp=datetime.now().isoformat()
    )

    # Send via email provider
    if email_manager.email_provider:
        success = email_manager.email_provider.send_email(
            to_email=verified_email,
            subject=f"Payment Receipt - Influencer Radar",
            html_content=receipt_html
        )
```

---

## 5. Account Recovery Flow

### Allow Users to Link Account on New Device

```python
def show_recovery_link_page():
    """Show page to recover account via verified email."""
    st.title("🔐 Recover Your Account")

    st.write("Using a new device? Link your account with your verified email.")

    with st.form("recovery_form"):
        email = st.text_input(
            "Enter your verified email",
            placeholder="you@example.com"
        )

        if st.form_submit_button("Send Recovery Link"):
            # Find user with this verified email
            # Send recovery link email
            # Link new session to existing user
            st.success("Recovery link sent to your email!")
```

---

## 6. Testing Locally

### Test Email Sending Without API

```python
# In secrets.toml, set test mode:
email_provider = "test"
```

Then tokens/links will be printed to console instead of sending emails:

```
TEST: Verification link: http://localhost:8501?verify_email=AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

### Manual Testing

1. Copy the verification link
2. Add to URL: `http://localhost:8501?verify_email=token_here`
3. Visit link
4. Email should be verified

### Using Mailhog (Local SMTP)

Install:

```bash
# macOS
brew install mailhog

# Run
mailhog  # Starts SMTP on :1025, Web UI on :8025
```

Configure:

```toml
email_provider = "smtp"
smtp_host = "localhost"
smtp_port = 1025
```

---

## 7. Testing Checklist

### Basic Testing

- [ ] App starts without email errors
- [ ] Email input widget shows in sidebar
- [ ] Can enter email address
- [ ] Click "Send Verification" button
- [ ] Verification email received (or link shown in test mode)
- [ ] Click verification link
- [ ] Email marked as verified ✅
- [ ] Badge shows "Verified ✅" in sidebar

### Advanced Testing

- [ ] Test with invalid email → error message
- [ ] Test expired link (24 hours) → error message
- [ ] Test already-used link → error message
- [ ] Test recovery flow → can link new device
- [ ] Test payment receipt sent to verified email

### Error Handling

- [ ] No API key set → graceful error, app continues
- [ ] Email send fails → user sees error, can retry
- [ ] Database error → fallback to session state

---

## 8. Production Deployment

### Before Deploying

1. **Remove Debug Panels**

   ```python
   # Comment out in app.py
   # if st.checkbox("🔧 Email Debug"):
   #     show_email_debug_panel(email_manager)
   ```

2. **Set Correct App URL**

   ```python
   app_url = "https://your-app-name.streamlit.app"
   ```

3. **Add API Key to Cloud Secrets**
   - For Streamlit Cloud: Settings → Secrets
   - Paste `secrets.toml` content

4. **Test on Cloud**
   - Deploy to Streamlit Cloud
   - Test email verification flow
   - Check logs for errors

5. **Monitor Logs**
   - Check for email sending failures
   - Monitor token expiration issues

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Create `apps/secrets.toml`:
   ```toml
   [secrets]
   sendgrid_api_key = "SG.your_api_key_here"
   email_provider = "sendgrid"
   ```
3. In Streamlit Cloud app settings → Secrets → paste content

---

## 9. Troubleshooting

### Email Not Sending

```
Check:
1. API key set in secrets.toml ✅
2. Email provider initialized (check logs)
3. Valid email address entered ✅
4. Email provider account has credits
5. Check email provider logs for errors
```

### Link Not Working

```
Check:
1. Correct verification link in email ✅
2. Token not expired (24-hour limit) ✅
3. Token not already used ✅
4. Query parameter correct: ?verify_email=token
5. Correct app URL in verification link
```

### Verification Not Persisting

```
Check:
1. PersistentUserManager initialized ✅
2. Email verification fields in user_data ✅
3. _save_user_data() called after verification ✅
4. Storage backend working (check debug panel)
```

---

## 10. API Reference

### EmailVerificationManager

```python
# Initialize
email_manager = EmailVerificationManager(provider="sendgrid")

# Request verification
success, message = email_manager.request_verification(
    email="user@example.com",
    user_id="user_123",
    app_url="https://myapp.com"
)

# Verify token
success, message, data = email_manager.verify_email(token)

# Check status
status = email_manager.get_verification_status(user_id)
# Returns: {"is_verified": True, "email": "...", "verified_at": "..."}

# Get verified email
email = email_manager.get_verified_email(user_id)
```

### PersistentUserManager Email Methods

```python
# Set verified email
user_manager.set_verified_email("user@example.com")

# Get email
email = user_manager.get_email()

# Check if verified
is_verified = user_manager.is_email_verified()

# Get verification status
status = user_manager.get_email_verification_status()
# Returns: {"email": "...", "is_verified": True, "verified_at": "..."}
```

---

## 11. Security Notes

### Token Security

✅ Tokens are:

- Cryptographically secure (256 bits)
- One-time use (marked after verification)
- Time-limited (24-hour expiration)
- Hashed in storage (HMAC-SHA256)

✅ Verification links are:

- Unique per email
- Not reusable
- Expire after 24 hours
- Include token in query parameter

### Email Security

⚠️ Remember:

- Use HTTPS in production
- Don't store passwords in email
- Use SendGrid/Resend (they use TLS)
- Consider encryption for highly sensitive data

---

## 12. Next Steps

1. **Immediate**: Set up email provider (SendGrid or Resend)
2. **Today**: Integrate email_manager.py into app.py
3. **This Week**: Test locally with mailhog
4. **Deploy**: Push to Streamlit Cloud, test in production

You now have a secure, optional email verification system! 🎉
