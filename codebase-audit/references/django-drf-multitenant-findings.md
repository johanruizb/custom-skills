# Django / DRF Multi-Tenant Audit Findings

Concrete findings from real multi-tenant Django/DRF audits. Use alongside `analysis-checklists.md` and `django-drf-performance-patterns.md`.

## Tenant Isolation Patterns

### IDOR: Unscoped get_object_or_404
**Pattern:** `get_object_or_404(Model, id=user_supplied_id)` without tenant FK filter.
**Evidence:** Search for `get_object_or_404(` followed by `id=` without `id_church=` or equivalent tenant field.
**Fix:** Always include tenant filter: `get_object_or_404(Model, id=id, id_church=church_instance)`.
**Risk:** High — cross-tenant data access. Attacker can enumerate IDs to read/modify data from other tenants.
**Pitfall:** Even when the model has an `id_church` FK, the view may not use it. Check every `get_object_or_404` call in multi-tenant views.

### IDOR: Unscoped .get(id=...)
**Pattern:** `Model.objects.get(id=user_supplied_id)` without tenant filter.
**Evidence:** Search for `.get(id=` or `.get(pk=` across all views and services.
**Fix:** Same as above — add tenant filter.
**Risk:** High.

### IDOR: Unscoped .filter(id=...) in update/delete
**Pattern:** `Model.objects.filter(id=id).update(...)` or `.delete()` without tenant filter.
**Evidence:** Search for `.filter(id=` followed by `.update(` or `.delete(`.
**Fix:** Add tenant filter to the queryset.

### Tenant Filter Coverage
**Check:** Count how many view files use `get_iglesia(request)` or equivalent tenant helper vs total view files. Files that don't use it may be:
- Public endpoints (intentional — verify they return minimal data)
- Admin-only endpoints (verify they're admin-only)
- Missing tenant isolation (bug)

## Rate Limiting

### Empty Throttle Configuration
**Pattern:** `DEFAULT_THROTTLE_CLASSES: []` and `DEFAULT_THROTTLE_RATES: {}` in DRF settings.
**Evidence:** Check `REST_FRAMEWORK` dict in settings files.
**Impact:** No rate limiting on any endpoint including login, registration, password reset.
**Mitigation:** Turnstile/CAPTCHA on login provides some bot protection but doesn't prevent credential stuffing at low rates.
**Fix:** Add `AnonRateThrottle`, `UserRateThrottle`, and `ScopedRateThrottle` for auth endpoints.

## Serializer Exposure

### fields = '__all__' Count
**Pattern:** `fields = '__all__'` in serializers.
**Evidence:** Search across all serializer files. Count occurrences.
**Impact:** Exposes all model fields including:
- Audit timestamps (`created_at`, `updated_at`)
- FK IDs (can leak tenant structure)
- Large text fields (performance)
- Potentially sensitive fields (PII, auth-related)
**Fix:** Replace with explicit field lists. Create separate serializers for list vs detail views.
**Pitfall:** The project's own conventions may explicitly ban `__all__`. Check AGENTS.md or project docs.

### Critical: Password Hash Exposure via fields='__all__' on User Model
**Pattern:** A serializer on the User model (or a model with a OneToOneField to User) uses `fields = '__all__'`, exposing the `password` field.
**Evidence:** Search for serializers that reference the User model AND use `fields = '__all__'`. The `password` field in Django stores the Argon2/bcrypt hash — it's not the plaintext password, but it enables offline cracking if leaked.
**Impact:** Critical — the password hash is returned in API responses. An attacker who gains read access to any user endpoint can extract all password hashes and attempt offline cracking.
**Fix:** Remove `password` from the serializer fields explicitly, or use an explicit field list that excludes it. Create a separate serializer for internal use if the password field is needed for write operations.
**Pitfall:** Even if the serializer is never imported or used in a view, the definition itself is a code smell. Check `grep -r "user_serializer\|UserSerializer"` to verify it's not used anywhere. If unused, remove the serializer entirely.
**Severity:** Critical
**Priority:** P0

## Debug Output in Production

### traceback.print_exc() Count
**Pattern:** `traceback.print_exc()` in view exception handlers.
**Evidence:** Search across all Python files. Count occurrences.
**Impact:** Leaks stack traces (file paths, local variables, DB query fragments) to stdout/logs.
**Fix:** Replace with `logger.exception()` for structured logging.
**Pitfall:** Use `logger.exception()` (not `logger.error()`) when replacing `traceback.print_exc()`. `logger.exception()` automatically captures the current exception context (traceback, message) and logs at ERROR level. `logger.error()` only logs the message string without the traceback. The pattern is:
```python
# Before
except Exception as e:
    traceback.print_exc()

# After
except Exception as e:
    logger.exception("Failed to process X: %s", str(e))
```

### print() in Production Code
**Pattern:** `print(` in view files, signals, utils.
**Evidence:** Search for `print(` excluding comments and management commands.
**Impact:** Outputs to stdout instead of structured logs. May log PII (request data, phone numbers, addresses).
**Fix:** Replace with `logger.debug()`, `logger.warning()`, or `logger.error()` as appropriate.

## External HTTP Calls

### Missing Timeout on External Requests
**Pattern:** `requests.post(url, data=...)` or `requests.get(url)` without `timeout=` parameter.
**Evidence:** Search for `requests.get(` and `requests.post(` without `timeout=` in the same call.
**Impact:** Request can hang indefinitely, blocking the Django worker thread.
**Fix:** Add `timeout=10` (or appropriate value) to all external HTTP calls.
**Pitfall:** Even calls to reliable services (Cloudflare Turnstile, Google APIs) should have timeouts.

## Public Endpoint Analysis

### AllowAny Endpoints
**Check:** List every view with `permission_classes = [AllowAny]`. For each:
- What data does it return? Should be minimal public fields only.
- Does it reveal tenant existence? (subdomain check, email check)
- Is it a logout endpoint? (acceptable — user may have expired token)
- Does it have rate limiting? (should have, since it's public)

### Subdomain/Tenant Existence Enumeration
**Pattern:** A public `AllowAny` endpoint that accepts a subdomain and returns whether it exists.
**Evidence:** Search for `AllowAny` views that query `Church.objects.filter(subdomain=...)` or similar.
**Impact:** Attacker can enumerate valid subdomains/tenants by observing 200 vs 404 responses.
**Severity:** Low — subdomains are often guessable anyway, but worth noting.
**Fix:** Return a generic response regardless of whether the subdomain exists (e.g., always return 200 with a generic message, or use a consistent error response).

### Username/Email Enumeration in Login
**Pattern:** Login endpoint has separate code paths for "user exists" vs "user does not exist" — different DB queries, different response timing, different status codes, or different error messages.
**Evidence:** Check login view for patterns like:
```python
try:
    user = User.objects.get(username=identifier)
except User.DoesNotExist:
    return Response({"error": "User not found"}, status=404)  # Enumeration!
```
**Impact:** Attacker can enumerate valid usernames/emails by observing response differences.
**Severity:** Medium — enables targeted credential stuffing and phishing.
**Fix:** Use a single code path that returns the same response regardless of whether the user exists. Use `check_password()` on a dummy hash when the user doesn't exist to normalize timing.

## WebSocket Security

### Accept-Before-Auth
**Pattern:** `await self.accept()` called before authentication in Channels consumers.
**Evidence:** Check consumer `connect` or `receive` methods for `accept()` before auth logic.
**Impact:** Unauthenticated connections held open (DoS vector).

### Token in Message Payload
**Pattern:** JWT sent as `{ type: 'auth', token: '...' }` in WebSocket message.
**Evidence:** Check frontend WebSocket connection code and backend consumer auth handler.
**Impact:** Token visible in message payloads (server logs, ws:// dev traffic).
**Fix:** Use `Sec-WebSocket-Protocol` header or query parameter on `wss://` URL.

## JWT Storage

### localStorage via Redux Persist
**Pattern:** `redux-persist` stores session reducer (containing `token` and `refreshToken`) in `localStorage`.
**Evidence:** Check Redux persist config and the persisted reducer keys.
**Impact:** Any XSS vulnerability gives attacker full access to long-lived refresh tokens.
**Fix:** Migrate refresh token to httpOnly cookie, access token to in-memory only.

## Django Settings Checklist for Multi-Tenant Apps

```python
# Required for production multi-tenant apps:
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Search Queries Summary

```bash
# IDOR patterns
rg "get_object_or_404\(" --include "*.py" -n | rg "id=" | rg -v "id_church="
rg "\.get\(id=" --include "*.py" -n | rg -v "id_church" | rg -v "test_"
rg "\.filter\(id=" --include "*.py" -n | rg -v "id_church" | rg -v "test_"

# Serializer exposure
rg "fields\s*=\s*['\"]__all__['\"]" --include "*.py" -n

# Debug output
rg "traceback\.print_exc\(" --include "*.py" -n
rg "^\s*print\(" --include "*.py" -n | rg -v "test_" | rg -v "management"

# External HTTP without timeout
rg "requests\.(get|post|put|delete)\(" --include "*.py" -n | rg -v "timeout"

# Rate limiting
rg "DEFAULT_THROTTLE" --include "*.py" -n

# Tenant helper usage
rg "get_iglesia\(" --include "*.py" -n | wc -l
rg "id_church=" --include "*.py" -n | wc -l

# AllowAny endpoints
rg "AllowAny" --include "*.py" -n

# WebSocket accept-before-auth
rg "await self\.accept\(\)" --include "*.py" -n -B 5

# JWT in localStorage
rg "redux-persist" --include "*.{js,jsx,ts,tsx}" -n -A 5
rg "localStorage" --include "*.{js,jsx,ts,tsx}" -n | rg "token\|jwt\|refresh"
```
