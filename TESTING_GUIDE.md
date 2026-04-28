# PersistentUserManager - Testing Guide

## Overview

This guide provides step-by-step testing procedures for the hybrid persistence system.

---

## Environment Setup

### Prerequisites

- Python 3.8+
- Streamlit installed
- `influencer-analyzer` project structure

### Quick Start

```bash
cd /Users/ad/Desktop/influencer-analyzer
streamlit run app.py
```

---

## Test Scenarios

### TEST 1: Basic Persistence (Page Refresh)

**Objective:** Verify data persists when user refreshes page

**Steps:**

1. Open app in browser: `http://localhost:8501`
2. Check Debug Info → Note User ID and Browser ID
3. Click "Analyze" button (any username)
4. Check sidebar metric: "Analyses Used" shows 1
5. **Refresh page (Ctrl+R or Cmd+R)**
6. Check sidebar metric again

**Expected Result:**

- ✅ "Analyses Used" still shows 1
- ✅ User ID and Browser ID unchanged
- ✅ No "User ID" change in Debug Info

**Failure Indicators:**

- ❌ Count resets to 0 after refresh
- ❌ User ID changes
- ✅ If this happens, check browser localStorage permissions

### TEST 2: Cross-Session Persistence

**Objective:** Verify data persists when browser is completely closed

**Steps (Localhost):**

1. Open app and verify state
2. Increment analysis count to 3
3. Record the User ID from Debug Info
4. **Completely close the browser**
5. Reopen browser and navigate to `http://localhost:8501`
6. Check Debug Info

**Expected Result:**

- ✅ Analysis count still shows 3
- ✅ **Same User ID as before**
- ✅ Payment history preserved
- ✅ Paid status remembered

**Note:** Streamlit Cloud may not retain filesystem data; session state + query params work instead.

### TEST 3: Browser Fingerprinting

**Objective:** Verify same browser gets same ID, different browser gets different ID

**Steps:**

1. Open app in Chrome, record User ID
2. Open app in Firefox, record User ID
3. Compare IDs

**Expected Result:**

- ✅ Chrome User ID ≠ Firefox User ID
- ✅ Each browser maintains its own separate data
- ✅ Incrementing in Chrome doesn't affect Firefox counts

**Private/Incognito Test:**

1. Open app in Chrome Incognito
2. Record User ID
3. Close private window
4. Reopen Chrome Incognito
5. Check User ID

**Expected Result:**

- ✅ New Private Window = New User ID
- ✅ Closing and reopening private mode = Different ID (browsers clear storage)

### TEST 4: Payment Tracking

**Objective:** Verify payment history persists

**Steps:**

1. Open app and check initial payment history (should be empty)
2. Use Debug Panel to simulate payment:
   ```python
   manager.add_payment_record(
       "test_payment_001",
       2.99,
       "analysis"
   )
   ```
3. Check Payment History section in sidebar
4. **Refresh page**
5. Check Payment History again

**Expected Result:**

- ✅ Payment appears in sidebar
- ✅ Payment persists after refresh
- ✅ Amount and type are correct

### TEST 5: Data Migration

**Objective:** Verify old session data migrates to persistent storage

**Setup:**

1. Manually set old session state variables:

   ```python
   import streamlit as st
   st.session_state.analyses_count = 5
   st.session_state.comparisons_count = 2
   st.session_state.is_paid_user = True
   ```

2. Initialize PersistentUserManager

**Expected Behavior:**

- ✅ Manager detects old data
- ✅ Migrates analyses_count (max of 5 or current)
- ✅ Migrates comparisons_count
- ✅ Migrates payment status
- ✅ Check logs show migration messages

**Verification:**

```python
manager = PersistentUserManager()
print(manager.get_analysis_count())  # Should be 5 or higher
print(manager.is_paid())  # Should be True
```

### TEST 6: Debug Panel Functionality

**Objective:** Verify debug utilities work correctly

**Steps:**

1. Check Debug Info checkbox
2. Copy the displayed User ID
3. Check "Storage Debug" checkbox
4. Review the "Storage Debug Panel" that appears

**Panel Features to Test:**

**6a. Reset User Data**

- Click "🔄 Reset User Data"
- Analysis count should become 0
- User ID should change (or stay same with `keep_user_id=True`)

**6b. Clear All Storage**

- Click "🗑️ Clear All Storage"
- Page refreshes
- All counts and payment history should be gone
- New User ID should be generated

**6c. Export Data**

- Click "📋 Copy JSON"
- Data should display as formatted JSON
- Should include: user_id, analyses_count, comparisons_count, payment_history
- Should be valid JSON (can paste in json validator)

### TEST 7: Multiple Tabs

**Objective:** Verify same user across multiple browser tabs

**Steps:**

1. Open app in Tab 1 (http://localhost:8501)
2. Increment analysis count to 3
3. **Open same URL in Tab 2**
4. Check analysis count in Tab 2 (should show 3)
5. Increment in Tab 2 to 4
6. Switch back to Tab 1 and refresh

**Expected Result:**

- ✅ Tab 2 shows count=3 initially (from persistent storage)
- ✅ Incrementing in Tab 2 changes to 4
- ✅ Tab 1 after refresh shows 4
- ✅ Both tabs share same User ID

**Note:** May show stale data in Tab 1 until refresh due to Streamlit's session model.

### TEST 8: Error Resilience

**Objective:** Verify app works even if storage fails

**Steps:**

1. Make filesystem read-only (if on localhost):

   ```bash
   chmod -r ~/.influencer_analyzer_cache
   ```

2. Try using app normally
3. Check error handling

**Expected Result:**

- ✅ App still functions
- ✅ Uses session_state as fallback
- ✅ Data persists in current session
- ✅ Check logs for warning messages

**Cleanup:**

```bash
chmod -rw+ ~/.influencer_analyzer_cache
```

---

## Streamlit Cloud Testing

### Deployment Test

**Steps:**

1. Deploy to Streamlit Cloud
2. Open app
3. Increment counts
4. Hard refresh (Cmd+Shift+R on Mac)
5. Check if data persists

**Expected Behavior:**

- ⚠️ Filesystem storage not available on Cloud
- ✅ Session state persistence works
- ✅ Query params persistence works (if configured)
- ✅ User data survives page refresh but not app restart

**Note:** For permanent storage on Cloud, you'd need a backend database.

---

## Automated Test Suite

### Run Unit Tests

```bash
python -m pytest tests/test_persistent_user_manager.py -v
```

### Run in Streamlit

Create `test_app.py`:

```python
import streamlit as st
from modules.persistent_user_manager import PersistentUserManager

st.title("Test Suite")

manager = PersistentUserManager()

# Test 1
if st.button("Test Persistence"):
    manager.increment_analysis_count()
    st.write(f"Incremented to: {manager.get_analysis_count()}")

# Test 2
if st.button("Test Reset"):
    old_id = manager.get_user_id()
    manager.reset_user_data(keep_user_id=True)
    new_id = manager.get_user_id()
    st.write(f"Reset - ID preserved: {old_id == new_id}")

# Test 3
if st.button("Export Data"):
    st.json(manager.get_session_summary())
```

Run with:

```bash
streamlit run test_app.py
```

---

## Troubleshooting

### Problem: Data not persisting

**Diagnosis:**

1. Check browser console (F12) for errors
2. Check localStorage is enabled
3. Run Debug Panel and check storage type

**Solutions:**

- Clear browser cache and try again
- Check filesystem permissions (if localhost)
- Verify browser_id is in URL query params

### Problem: Different User ID each refresh

**Diagnosis:**

- Browser fingerprinting not working
- Query params not persisting

**Solutions:**

1. Check URL has `?browser_id=...` parameter
2. Verify st.query_params is being used
3. Try private/incognito window for fresh test

### Problem: Payment history lost

**Diagnosis:**

1. Check if storage is working (Test 1)
2. Verify payment_history field exists in user_data

**Solutions:**

```python
manager = PersistentUserManager()
print(manager.get_session_summary())  # Check all fields
print(manager.export_user_data())     # Full export
```

### Problem: Migration didn't work

**Diagnosis:**

- Old session data wasn't detected
- Migration logic didn't trigger

**Solutions:**

1. Check logs for migration messages
2. Manually verify old session state:
   ```python
   import streamlit as st
   print(st.session_state.keys())
   ```
3. Force migration by checking browser_id changed

---

## Performance Benchmarks

Expected metrics:

| Operation          | Time    | Expected   |
| ------------------ | ------- | ---------- |
| Initialize manager | < 50ms  | Fast       |
| Get user_id        | < 5ms   | Instant    |
| Increment count    | < 20ms  | Fast       |
| Save data          | < 100ms | Acceptable |
| Reset data         | < 50ms  | Fast       |

If operations exceed these times, check:

- Filesystem I/O (localStorage simulator)
- Number of items in storage
- Streamlit app performance

---

## Checklist for Production

- [ ] All 8 tests pass
- [ ] No warnings in logs during normal use
- [ ] Payment history persists
- [ ] User IDs are consistent per browser
- [ ] Debug panels removed from production
- [ ] Error handling tested
- [ ] Works on both localhost and Cloud
- [ ] Migration tested with old session data
- [ ] Multiple browser testing complete
- [ ] Load testing done (if high traffic expected)

---

## Reporting Issues

When reporting issues, include:

1. Full test case (steps to reproduce)
2. Expected vs actual behavior
3. Browser and OS information
4. Full debug export:
   ```python
   manager = PersistentUserManager()
   print(manager.get_debug_info())
   ```
5. Relevant log messages
