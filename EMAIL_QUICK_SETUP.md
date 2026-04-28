# Email Verification - Quick Setup

## 1 Min Setup

### Install Provider

```bash
# Choose ONE:
pip install sendgrid     # Option A
pip install resend       # Option B
```

### Add API Key

Create `.streamlit/secrets.toml`:

```toml
sendgrid_api_key = "SG.your_key_here"
# OR
resend_api_key = "re_your_key_here"
email_provider = "sendgrid"  # or "resend"
```

### Integrate in app.py

```python
# 1. Import
from modules.email_manager import EmailVerificationManager
from modules.email_ui import show_email_verification_widget, handle_verification_link

# 2. Initialize (after user_manager)
email_manager = EmailVerificationManager(
    provider=st.secrets.get("email_provider", "sendgrid")
)

# 3. Handle links (before sidebar)
handle_verification_link(email_manager, user_manager)

# 4. Show widget (in sidebar)
show_email_verification_widget(user_manager, email_manager)
```

---

## 5 Min Local Testing

### Option A: Print Links to Console

```toml
# In secrets.toml - no API key = test mode
email_provider = "sendgrid"  # Will print links instead
```

Then when user sends verification:

```
TEST: Verification link: http://localhost:8501?verify_email=token_here
```

Copy link, visit in browser, email verified ✅

### Option B: Use Mailhog

```bash
# Install
brew install mailhog

# Run (starts web UI on localhost:8025)
mailhog

# Configure app
# secrets.toml already configured for SendGrid/Resend
# App will send to Mailhog SMTP
```

---

## Files Created

```
modules/email_manager.py      - Core email logic
modules/email_ui.py           - Streamlit components
EMAIL_INTEGRATION_GUIDE.md    - Full integration guide
EMAIL_QUICK_SETUP.md          - This file
```

---

## Key Features

✅ One-time verification links (24-hour expiration)
✅ Secure token generation (256-bit, hashed)
✅ Account recovery on new devices
✅ Automatic payment receipts
✅ Optional (doesn't break if not configured)
✅ Works with SendGrid or Resend
✅ Test mode (print links to console)

---

## Verification Flow

```
User enters email
  ↓
Click "Send Verification"
  ↓
Verification email sent
  ↓
User clicks link in email
  ↓
Token validated
  ↓
Email marked as verified ✅
  ↓
Can now recover account on new devices
  ↓
Payment receipts sent automatically
```

---

## Testing

```bash
# 1. Start app
streamlit run app.py

# 2. In browser sidebar
#    - Enter test email
#    - Click "Send Verification"
#    - Check console or email

# 3. Click verification link
#    - Should show success message
#    - Sidebar shows "✅ Verified"

# 4. Done! ✅
```

---

## Troubleshooting

### "Email provider not initialized"

→ Check API key in secrets.toml

### "Verification email sent!" but no email received

→ Check email provider account/credits
→ Check spam folder
→ Use test mode to see link

### Email not persisting as verified

→ Check browser storage is enabled
→ Verify persistent_user_manager is initialized
→ Check debug panel

---

## No API Key Testing

Want to test without an API key?

```python
# In app.py
email_manager = EmailVerificationManager(provider="test")

# Now verification links print to console instead of sending
```

---

## Production Checklist

- [ ] API key added to secrets.toml
- [ ] Email provider account created (SendGrid/Resend)
- [ ] Tested locally
- [ ] Tested verification flow end-to-end
- [ ] Debug panels removed/disabled
- [ ] Deployed to Streamlit Cloud
- [ ] Secrets added to Cloud settings
- [ ] Tested on live deployment
- [ ] Monitored logs for errors

---

## API Quick Reference

```python
# Initialize
email_manager = EmailVerificationManager()

# Send verification
success, msg = email_manager.request_verification(
    "user@example.com",
    "user_123"
)

# Verify token
success, msg, data = email_manager.verify_email(token)

# Check status
status = email_manager.get_verification_status("user_123")
# → {"is_verified": True, "email": "...", "verified_at": "..."}

# User manager integration
user_manager.set_verified_email("user@example.com")
user_manager.is_email_verified()  # → True
user_manager.get_email()  # → "user@example.com"
```

---

## That's It!

You now have email verification in your Streamlit app. Users can optionally verify to recover accounts and get payment receipts. 🎉

Next: Read EMAIL_INTEGRATION_GUIDE.md for advanced features like account recovery and payment receipts.
