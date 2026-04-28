# Architecture: Hybrid Session + Local Storage Persistence

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Application (Server)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         PersistentUserManager (Main Class)                │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  • Browser ID generation                                  │   │
│  │  • Data initialization & migrations                       │   │
│  │  • Public API (get_*, increment_*, set_*, add_*)         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ▲                                    │
│                              │                                    │
│  ┌──────────────────────────┴────────────────────────────────┐   │
│  │      LocalStorageSimulator (Storage Abstraction)          │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  • Unified storage interface                             │   │
│  │  • Multiple backends (session, filesystem, query params) │   │
│  │  • Automatic backend selection                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│            ▲           ▲           ▲          ▲                  │
│            │           │           │          │                  │
│         ┌──┴──┐  ┌──────┴──┐  ┌──┴──┐  ┌────┴────┐             │
│         │      │  │         │  │      │  │          │             │
│         ▼      ▼  ▼         ▼  ▼      ▼  ▼          ▼             │
│      Session  Filesys   Query   Browser   Migration Logic        │
│      State    Storage   Params  Fingerprint                       │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘
         │                                           │
         │                                           │
         └─────────────────────────────────────────┘
                            │
                            ▼
                 ┌───────────────────┐
                 │  Browser Storage  │
                 │  (Client-Side)    │
                 │  • LocalStorage   │
                 │  • SessionStorage │
                 │  • Query Params   │
                 └───────────────────┘
```

---

## Components Deep Dive

### 1. BrowserFingerprint Class

**Purpose:** Generate consistent browser identifiers without requiring authentication

**Algorithm:**

```
BrowserFingerprint.generate_fingerprint():
  1. Check query_params for "browser_id" parameter
  2. If found, return existing browser_id
  3. If not found:
     - Combine: Streamlit session ID + URL
     - Hash with SHA256
     - Return first 16 characters
```

**Why This Works:**

- Same browser → Same fingerprint (deterministic)
- Different browser/incognito → Different fingerprint
- Survives page reloads (Streamlit maintains session ID)
- No cookies or external tracking needed

**Limitations:**

- Clears in private/incognito windows (by design)
- Users on shared devices share same ID (acceptable trade-off)
- Vulnerable to device fingerprinting detection (privacy concern)

### 2. LocalStorageSimulator Class

**Purpose:** Provide unified storage interface with multiple backends

**Storage Backends (Priority Order):**

1. **Session State (Primary)**
   - Location: Python dict in `st.session_state`
   - Speed: Fastest (in-memory)
   - Lifespan: Current session only (~30 min)
   - Availability: 100%
   - Cloud Support: Yes

2. **Filesystem (Secondary - Localhost)**
   - Location: `~/.influencer_analyzer_cache/`
   - Speed: Fast (disk I/O)
   - Lifespan: Until cleared
   - Availability: Localhost only
   - Cloud Support: No

3. **Query Parameters (Tertiary)**
   - Location: URL `?browser_id=...`
   - Speed: Automatic with st.query_params
   - Lifespan: Current session
   - Availability: Limited to query string size
   - Cloud Support: Yes

**Storage Key Structure:**

```
influencer_analyzer_{browser_id}_{data_key}

Example:
  influencer_analyzer_a1b2c3d4e5f6g7h8_user_data
  influencer_analyzer_a1b2c3d4e5f6g7h8_last_payment
```

**Write Path:**

```
set_item(browser_id, key, value):
  1. Store in st.session_state (always)
  2. Try store to filesystem (if localhost)
  3. Implicit: query_params managed by Streamlit
```

**Read Path:**

```
get_item(browser_id, key):
  1. Check st.session_state (fast hit)
  2. If miss: check filesystem
  3. If found in filesystem: sync to session_state
  4. Return value or None
```

### 3. PersistentUserManager Class

**Purpose:** Business logic layer for user data management

**Data Schema:**

```python
{
    "version": 1,                          # For future migrations
    "user_id": "user_a1b2c3d4e5f6g7h8",   # Persistent ID
    "created_at": "2026-04-28T...",       # Account creation
    "last_accessed": "2026-04-28T...",    # Last activity
    "analyses_count": 0,                   # Total analyses
    "comparisons_count": 0,                # Total comparisons
    "is_paid_user": false,                 # Payment status
    "payment_history": [                   # Payment records
        {
            "payment_id": "stripe_12345",
            "amount": 2.99,
            "type": "analysis",
            "status": "completed",
            "timestamp": "2026-04-28T..."
        }
    ]
}
```

**Initialization Flow:**

```
__init__:
  1. Get/create browser ID
  2. Call _init_user_data()
     → Check storage for existing data
     → If missing: create new with defaults
     → Sync to session_state
  3. Call _perform_migrations()
     → Look for old session data
     → Merge if found (take max values)
     → Mark migration complete
```

**Data Save Pattern:**

```
All mutation methods follow this pattern:
  1. Get current data: data = self._get_user_data()
  2. Modify: data[field] += delta
  3. Save: self._save_user_data()

This ensures:
  • No data corruption
  • Atomic writes
  • Consistent timestamps
```

---

## Persistence Guarantees

### Session Level (Current Browser Session)

| Scenario                    | Persistence | Status                        |
| --------------------------- | ----------- | ----------------------------- |
| Page refresh                | ✅ Yes      | Session state survives        |
| Browser tab switch          | ✅ Yes      | State synchronized            |
| Hard refresh (Ctrl+Shift+R) | ✅ Yes      | Filesystem/storage syncs back |

### Cross-Session (Same Browser, New Session)

| Scenario        | Localhost  | Cloud      | Status                                                 |
| --------------- | ---------- | ---------- | ------------------------------------------------------ |
| Browser restart | ✅ Yes     | ⚠️ Limited | Filesystem (local) or query params                     |
| Cache clear     | ⚠️ Partial | ⚠️ Limited | User ID lost, data preserved if browser_id recoverable |
| Private window  | ❌ No      | ❌ No      | Each private window = new user                         |

### Cross-Browser

| Scenario         | Result                                   |
| ---------------- | ---------------------------------------- |
| Chrome ↔ Firefox | Different users (separate storage)       |
| Desktop ↔ Mobile | Different users (different fingerprints) |
| Shared device    | Same user (same fingerprint)             |

---

## Error Handling Strategy

### Failure Scenarios

**1. Filesystem Unavailable**

```
Scenario: ~/.influencer_analyzer_cache not writable
Response:
  - Log warning (non-critical)
  - Fall back to session_state
  - Continue normally
Result: Data persists in current session only
```

**2. Storage Quota Exceeded**

```
Scenario: Browser storage full (unlikely, max ~10MB)
Response:
  - Log error
  - Fall back to session_state
  - Try to write on next save
Result: No data loss, graceful degradation
```

**3. Corrupted Data**

```
Scenario: JSON parsing fails
Response:
  - Log error with details
  - Use fallback/empty defaults
  - Mark for review in debug panel
Result: App continues with fresh data
```

**4. Browser ID Generation Fails**

```
Scenario: Streamlit session data unavailable
Response:
  - Use emergency fallback ID
  - Generate from MD5 hash
  - Log warning
Result: Less consistent but app works
```

---

## Performance Characteristics

### Initialization Cost

```
First Run:     ~50ms (create new user, write to storage)
Subsequent:    ~20ms (read from session state, sync from storage)
Worst Case:    ~100ms (filesystem I/O + migration)
```

### Operations Per Second

```
get_* operations:      ~5000 ops/sec (in-memory)
increment_*:          ~1000 ops/sec (with save)
save_user_data():      ~500 ops/sec (filesystem) / ~5000 (session)
```

### Memory Footprint

```
Per user: ~5-10 KB (data + overhead)
1000 users: ~5-10 MB total
Acceptable: Well under Streamlit limits
```

---

## Security Considerations

### Data Exposure

**Public Data (Acceptable Risk):**

- User ID (pseudo-anonymous)
- Analysis count (non-sensitive)
- Paid status (non-sensitive)

**Sensitive Data (Minimal Risk):**

- Payment history (stored client-side)
- Browser ID (not transmitted)

**Recommendations:**

1. Don't store PII (credit card #s, phone)
2. Stripe handles actual payment data
3. Use HTTPS in production
4. Consider field-level encryption if sensitive data added

### Privacy Concerns

**Browser Fingerprinting:**

- Pro: No cookies, user-transparent
- Con: Could identify user across sites
- Mitigation: Use only for session tracking, not cross-site

**localStorage Persistence:**

- Cleared automatically on browser cache clear
- Accessible to any script on same domain
- Acceptable for analytics use case

---

## Migration Strategy

### Version 1 → Version 2 (Future)

```python
def _perform_migrations(self):
    version = self._get_user_data()["version"]

    if version == 1:
        # Perform v1→v2 migration
        data = self._get_user_data()
        # ... transformation ...
        data["version"] = 2
        self._save_user_data()
```

### Legacy Session Data

**Scenario:** User with old non-persistent session data returns

**Migration Process:**

1. Check for old keys in st.session_state
2. If found and higher values:
   ```python
   current_data["analyses_count"] = max(
       current_data["analyses_count"],
       st.session_state.get("analyses_count", 0)
   )
   ```
3. Save migrated data
4. Mark migration complete

---

## Cloud Deployment Considerations

### Streamlit Cloud

**Limitations:**

- No persistent filesystem (container ephemeral)
- Session state survives page reload
- Query params can persist across redirects

**Workaround:**

- Use session state as primary storage
- Browser_id stored in query params
- User ID remains consistent within session

**For True Persistence on Cloud:**

- Add backend database (PostgreSQL, MongoDB)
- Use authentication (email, OAuth)
- Cloud storage (S3, Google Cloud Storage)

### Localhost

**Full Capabilities:**

- Session state (works)
- Filesystem storage (works)
- Query params (works)
- All three backends operational

---

## Testing Strategy

### Unit Tests

- Browser fingerprint consistency
- Storage backend failover
- Data schema validation
- Migration logic

### Integration Tests

- Full user flow (init → use → persist)
- Cross-session state recovery
- Multiple tab synchronization
- Error recovery

### End-to-End Tests

- Localhost deployment
- Cloud deployment
- Browser testing (Chrome, Firefox, Safari)
- Device testing (Desktop, Mobile)

---

## Future Enhancements

1. **Backend Database Integration**
   - Add optional PostgreSQL/MongoDB support
   - Enable true cross-device persistence
   - Support user authentication

2. **Encryption**
   - Encrypt sensitive fields at rest
   - Use browser crypto API

3. **Analytics**
   - Track user cohorts
   - Measure retention
   - Analyze feature usage

4. **Sync**
   - Multi-tab real-time sync
   - Conflict resolution for concurrent edits
   - Vector clock versioning

5. **Quota Management**
   - Enforce storage limits per user
   - Cleanup old data
   - Archive historical data
