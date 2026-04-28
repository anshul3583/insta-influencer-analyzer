# Integration Guide: PersistentUserManager

## Overview

Replace `UserManager` with `PersistentUserManager` for hybrid session + local storage persistence.

---

## Changes Required in `app.py`

### 1. Update Imports (Line 6)

**BEFORE:**

```python
from modules.user_manager import UserManager
```

**AFTER:**

```python
from modules.persistent_user_manager import PersistentUserManager, show_persistent_debug_panel
```

---

### 2. Update Manager Initialization (Line 49)

**BEFORE:**

```python
user_manager = UserManager()
```

**AFTER:**

```python
user_manager = PersistentUserManager()
```

**That's it!** The API is backward compatible, so the rest of the code works unchanged.

---

## Enhanced Debug Panel (Optional Enhancement)

### Location: In the Sidebar Debug Section (Around Line 113-120)

**BEFORE:**

```python
if st.checkbox("🔍 Debug Info"):
    st.code(f"""
User ID: {user_id}
Analyses: {user_manager.get_analysis_count()}
Comparisons: {user_manager.get_comparison_count()}
Is Paid: {user_manager.is_paid()}
Session: {user_manager.get_session_summary()}
    """)
```

**AFTER:**

```python
if st.checkbox("🔍 Debug Info"):
    # Simple view
    st.code(f"""
User ID: {user_id}
Browser ID: {user_manager.get_browser_id()[:8]}...
Analyses: {user_manager.get_analysis_count()}
Comparisons: {user_manager.get_comparison_count()}
Is Paid: {user_manager.is_paid()}
Persistence: ✅ Hybrid (Session + Storage)
Session: {user_manager.get_session_summary()}
    """)

# Advanced debug panel (development only)
if st.checkbox("🔧 Advanced Storage Debug"):
    show_persistent_debug_panel()
```

---

## Additional Notes

### Backward Compatibility

- `PersistentUserManager` has the same public API as `UserManager`
- All existing code using `user_manager.method_name()` continues to work
- Data automatically migrates from old sessions if they exist

### Features Added

1. **Persistent User IDs** - Same user_id across browser sessions
2. **Storage Fallback** - Session → Filesystem → Query params
3. **Browser Fingerprinting** - Consistent identification without cookies
4. **Migration Logic** - Preserves old session data automatically
5. **Debug Tools** - Built-in utilities for development

### Testing the Integration

**Test 1: Data Persistence**

1. Load the app
2. Click "Analyze" to increment count
3. Refresh the page → **Count should persist**
4. Close browser and reopen → **Count should persist**

**Test 2: Browser Fingerprinting**

1. Check the Debug Info panel
2. Note the User ID and Browser ID
3. Refresh page → **IDs should stay the same**
4. Open in private/incognito → **New IDs generated**

**Test 3: Migration**

1. If you had old session data, run the debug panel
2. Check that old data was migrated automatically
3. Old counts should appear in the new persistent system

---

## Configuration & Customization

### Change Storage Location

Edit in `persistent_user_manager.py`:

```python
class LocalStorageSimulator:
    CACHE_DIR = Path.home() / ".influencer_analyzer_cache"  # Change this path
```

### Disable Filesystem Storage (Cloud-only)

The system auto-detects and only uses filesystem on localhost.
For Cloud deployments, it automatically uses only session state.

### Custom Data Fields

Add to `_init_user_data()` method in `PersistentUserManager`:

```python
user_data = {
    # ... existing fields ...
    "custom_field": default_value,  # Add here
}
```

---

## Production Checklist

- [ ] Test on localhost
- [ ] Test on Streamlit Cloud
- [ ] Verify data persists across page refreshes
- [ ] Verify user IDs are consistent per browser
- [ ] Test migration of old session data
- [ ] Remove debug panels before deploying
- [ ] Monitor logs for persistence errors

---

## Troubleshooting

### User ID changes on each reload?

- Clear browser cache and try again
- Check that query params are persisting (browser_id in URL)

### Data not persisting?

- Check browser console for errors
- Verify localStorage is not disabled
- Check Streamlit Cloud storage permissions

### Migration not working?

- Check debug panel for migration logs
- Ensure old session data exists in st.session_state
- Run `user_manager.reset_user_data()` to test

---

## Testing Code Snippet

```python
# Quick test in development
def test_persistence():
    manager = PersistentUserManager()

    # Test incrementing
    manager.increment_analysis_count()
    count_1 = manager.get_analysis_count()

    # Simulate page reload by creating new manager
    manager2 = PersistentUserManager()
    count_2 = manager2.get_analysis_count()

    assert count_1 == count_2, "Persistence failed!"
    print("✅ Persistence test passed")
```

Run this in a Streamlit script to verify the integration works.
