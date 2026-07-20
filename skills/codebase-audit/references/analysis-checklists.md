# Analysis Checklists

Detailed checklists for each audit area. Use these during Phase 5 (Audit) to systematically review each module.

## Performance Checklist

### Database & Data Access
- [ ] N+1 query patterns (query inside a loop)
- [ ] Missing indexes on frequently filtered/joined columns
- [ ] Inefficient queries (SELECT *, unnecessary JOINs, missing WHERE)
- [ ] Missing pagination on large result sets
- [ ] Lack of query result caching
- [ ] Unbounded queries (no LIMIT)
- [ ] Synchronous DB calls in hot paths
- [ ] Missing connection pooling
- [ ] Transaction scope too wide (holding connections/locks unnecessarily)
- [ ] ORM misuse (lazy loading triggering unexpected queries)

### Algorithms & Data Structures
- [ ] O(n²) or worse algorithms where O(n) or O(n log n) suffices
- [ ] Linear search where hash map / set lookup would work
- [ ] Recursion without memoization on repeated subproblems
- [ ] Repeated computation of the same value (no caching/memoization)
- [ ] Inefficient string concatenation in loops (use StringBuilder/buffer)
- [ ] List where Set/Dedup structure would be more appropriate
- [ ] Sorting when only min/max needed

### Memory
- [ ] Large objects held in memory longer than needed
- [ ] Memory leaks (event listeners not removed, timers not cleared, closures capturing large scope)
- [ ] Unnecessary deep copies where references suffice
- [ ] Large arrays/buffers allocated but partially used
- [ ] Missing stream/lazy processing for large data
- [ ] Object pools missing for frequently allocated/deallocated objects

### Concurrency & Parallelism
- [ ] Blocking I/O on main/critical thread (should be async/worker)
- [ ] Missing parallelism for independent operations (sequential where parallel possible)
- [ ] Lock contention on hot paths
- [ ] Unnecessary synchronization on read-only data
- [ ] Thread/process pool misconfigured (too many/few workers)
- [ ] Missing backpressure handling for streams/queues

### Rendering & I/O
- [ ] Unnecessary re-renders (React: missing memo/useMemo, Vue: missing computed)
- [ ] Layout thrashing (read-write DOM in loop)
- [ ] Missing virtualization for large lists
- [ ] Images not optimized/resized/lazy-loaded
- [ ] Excessive HTTP requests (missing batching, missing HTTP/2)
- [ ] Missing compression (gzip/brotli) on responses
- [ ] Missing CDN for static assets
- [ ] Synchronous file I/O in request paths

### Caching
- [ ] Missing cache layer for frequently read, rarely changed data
- [ ] Cache invalidation bugs (stale data served)
- [ ] Cache too aggressive (memory waste or stale data)
- [ ] Cache key collisions
- [ ] Missing ETag/Last-Modified for conditional requests

### Configuration
- [ ] Debug mode enabled in production config
- [ ] Missing production optimizations (minification, tree-shaking, source maps in prod)
- [ ] Inefficient serializer configured (e.g., JSON where protobuf/MessagePack better)
- [ ] Connection pool sizes not tuned
- [ ] Worker/process count not tuned to CPU cores
- [ ] Missing HTTP keep-alive

### Framework/Language Specific
- [ ] Python: missing __slots__ for many instances, list vs generator, GIL-aware design
- [ ] Node.js: event loop blocking, missing stream usage, Buffer vs string
- [ ] Go: goroutine leaks, missing context cancellation, slice preallocation
- [ ] Rust: unnecessary clones, missing &str vs String, missing zero-copy
- [ ] Java: unnecessary autoboxing, missing StringBuilder, synchronized overuse
- [ ] Detect language from Phase 2 and apply language-specific checks

#### React / Frontend Performance (add to any React SPA audit)

- [ ] **Heavy library statically imported when only used on one page** — check for `three.js`, `framer-motion`, `react-helmet`, `qrcode`, `react-signature-canvas`, `jspdf`, `html-to-image`, `html5-qrcode` in static imports. Each should be lazy-loaded via `React.lazy()` or dynamic `import()` if only used on a single route or behind a user action.
- [ ] **Barrel imports from MUI** — search for `from "@mui/material"` (barrel). Each barrel import prevents tree-shaking. Should be `from "@mui/material/Button"` etc. Check project ESLint config for `no-restricted-imports` rule.
- [ ] **`key={index}` in list renders** — search for `key={index}` in `.map()` calls. Array index as key causes React to reuse DOM nodes incorrectly on reorder/insert/delete. Should use stable unique IDs from data.
- [ ] **`useEffect` missing dependency array or suppressed `exhaustive-deps`** — search for `eslint-disable.*exhaustive-deps`. Each suppression is a potential stale closure or missing re-run. Review each: mount-only effects should use a `useMount` hook; effects with intentionally omitted deps need a comment.
- [ ] **No `AbortController` in async `useEffect`** — search for `useEffect` with `async` or `.then()` inside. Without `AbortController`, in-flight requests continue after unmount, causing setState-after-unmount warnings and potential race conditions where stale responses overwrite fresh data.
- [ ] **`manualChunks` not wired into Vite/Rollup config** — check if a `manualChunks.js` helper exists but `vite.config.js` has no `build.rollupOptions.output.manualChunks`. Dead code or suboptimal chunking.
- [ ] **Large components exceeding project line limit** — check for files >500 lines (or project's stated limit). Large components have more re-render surface, harder to `React.memo`, and often contain inline object/array literals recreated every render.
- [ ] **`framer-motion` used for simple CSS transitions** — check if `framer-motion` is imported in 10+ files for simple fade/slide animations that could use CSS transitions or MUI `Fade`/`Grow`/`Slide` components instead.
- [ ] **`react-helmet` in bootstrap entry point** — check `main.jsx` or entry file for `import { Helmet } from "react-helmet"`. This forces the library into the initial bundle. Defer to a component inside the app tree.
- [ ] **`window.open()` for blob URLs without `noopener,noreferrer`** — search for `window.open(url, "_blank")` without third argument. While blob URLs are same-origin, inconsistent security posture.
- [ ] **`useState` for server data instead of SWR/React Query** — check if components use `useState` + `useEffect` for API data instead of a caching library. SWR/React Query provide deduplication, caching, revalidation, and cancellation.
- [ ] **Missing `React.memo` on frequently re-rendered list items** — check if list item components (inside `.map()`) are wrapped in `React.memo`. Without it, every parent re-render re-renders all list items.
- [ ] **Inline function/object/array literals in JSX props** — search for patterns like `onClick={() => ...}` or `style={{...}}` or `options={[...]}` inside render. These create new references every render, defeating `React.memo` and `PureComponent`.
- [ ] **Missing code splitting on route level** — check if route components use `React.lazy()` + `Suspense`. Without it, all page code is in the initial bundle.
- [ ] **`<img>` tags without lazy loading** — search for `<img` without `loading="lazy"`. Images above the fold should use native lazy loading.
- [ ] **Large static data arrays defined inside component body** — check for `const options = [...]` or `const config = {...}` inside the component function. These are recreated every render. Extract outside the component or use `useMemo`.
- [ ] **Missing `useCallback` on callbacks passed to child `React.memo` components** — search for callbacks defined inline in render that are passed to memoized children. Without `useCallback`, the child receives a new reference every render and `memo` is defeated.

#### Django / DRF Performance (add to any Django audit)

- [ ] **No pagination** — check `REST_FRAMEWORK` settings for `DEFAULT_PAGINATION_CLASS` and `PAGE_SIZE`. Also check every `ModelViewSet` and `ListAPIView` for `pagination_class = None` (intentional) vs missing (unbounded results).
- [ ] **No caching layer** — check `CACHES` in settings. If Redis is available (e.g., for Channels) but `CACHES` is absent, every request hits the DB for lookup tables, church metadata, and config. Check for zero `cache.get`/`cache.set` calls.
- [ ] **`fields = '__all__'` in serializers** — count occurrences. Each one serializes every model column including large text fields, audit timestamps, and potentially sensitive data. Prefer explicit field lists.
- [ ] **N+1 queries in view loops** — search for `for .* in .*serializer.data` or `for .* in .*queryset` followed by `.get()`, `.filter()`, `.count()`, or `.all()` inside the loop body. Classic pattern: serialize queryset, then iterate `serializer.data` and re-fetch related objects per item.
- [ ] **N+1 count queries** — search for `.count()` inside `for` loops. Batch-count with `annotate(Count(...))` or `values(...).annotate(...)` instead.
- [ ] **`.count() != 0` where `.exists()` suffices** — `.exists()` issues `SELECT 1 LIMIT 1` (stops at first match); `.count()` scans all matching rows. Search for `if .count() > 0`, `if .count() != 0`, `while .count()`.
- [ ] **Missing `select_related` / `prefetch_related`** — search for FK/M2M access inside loops without prefetch. Check that `Prefetch` with `to_attr` is used when the loop re-filters (`.filter()` on a prefetched relation invalidates the cache).
- [ ] **Recursive tree traversal with per-node queries** — check for recursive functions that call `.filter(parent=X)` or `.children.filter()` per node. Fetch all nodes in one query and build the tree in memory.
- [ ] **`.save()` in loops instead of `bulk_create`/`bulk_update`** — each `.save()` is a separate INSERT/UPDATE. Use `bulk_create(batch_size=500)` and `bulk_update(fields=[...])`.
- [ ] **Duplicate `.count()` calls** — check for `queryset.count()` called multiple times in the same function where the result doesn't change. Cache in a variable.
- [ ] **Synchronous HTTP calls in request path** — search for `requests.get`/`requests.post` in views, utils, and services called from views. These block the Django worker. Check for missing timeouts (block indefinitely). Consider async tasks or caching.
- [ ] **Missing `.only()` / `.defer()` on wide models** — check if list endpoints on models with 20+ fields use `.only()` to fetch only needed columns. Without it, all columns are loaded from DB.
- [ ] **Missing composite indexes** — check if `Meta.indexes` is defined. For multi-tenant apps, common filter patterns (`id_church + status`, `id_church + deleted`, `id_church + person_type`) need composite indexes. Django auto-indexes FK columns but not compound filters.
- [ ] **Missing ETag/Last-Modified** — check for `@condition` decorator or `ETag`/`Last-Modified` response headers on read-only endpoints. Without them, every request returns full data even for unchanged resources.
- [ ] **Connection pool not configured** — check `conn_max_age` in `DATABASES`. With ASGI/uvicorn and many workers, persistent connections can exhaust PostgreSQL's `max_connections` without a pooler (PgBouncer).
- [ ] **Debug `print()` in production views** — search for `print(` in view files. These output to stdout instead of structured logs and may trigger unnecessary queries just for debug output.
- [ ] **Email/SMTP connection per message** — check if email sending opens a new `smtplib.SMTP` connection per email. For batch notifications, reuse one connection for multiple messages.
- [ ] **Bulk import without `batch_size`** — check `bulk_create` calls for missing `batch_size` parameter. Without it, all INSERTs go in one query, risking PostgreSQL parameter limit errors for wide tables.

---

## Bugs Checklist

### Logic Errors
- [ ] Off-by-one errors in loops/bounds
- [ ] Incorrect boolean logic (AND vs OR, De Morgan violations)
- [ ] Wrong comparison operator (= vs ==, < vs <=)
- [ ] Incorrect default values
- [ ] Mutable default arguments (Python: def f(x=[]))
- [ ] Floating point comparison without epsilon
- [ ] Integer overflow/underflow not handled
- [ ] Sign errors in arithmetic
- [ ] Null/undefined/None dereference paths
- [ ] Incorrect null/empty checks (falsy vs null vs undefined vs None)

### Edge Cases
- [ ] Empty collection / empty string / empty input not handled
- [ ] Single-element collection edge case
- [ ] Very large input (overflow, timeout, OOM)
- [ ] Unicode/encoding edge cases (BOM, combining chars, different encodings)
- [ ] Timezone and DST handling
- [ ] Leap year / date boundary handling
- [ ] Concurrent modification during iteration
- [ ] Zero / negative values where positive expected
- [ ] Maximum/minimum boundary values

### Error Handling
- [ ] Empty catch/except blocks (swallowed errors)
- [ ] Catching too broad exception (catch Exception, except:)
- [ ] Catching and re-throwing without context (losing stack trace)
- [ ] Missing error handling on I/O (file, network, DB)
- [ ] Error handling that masks the original error
- [ ] Inconsistent error handling patterns across modules
- [ ] Errors not propagated to caller
- [ ] Missing rollback/cleanup in error paths (resource leaks on failure)

### State & Consistency
- [ ] Race conditions (shared mutable state without synchronization)
- [ ] Inconsistent state after partial failure
- [ ] Global mutable state modified without synchronization
- [ ] State not validated after deserialization
- [ ] Stale references to deleted/modified objects
- [ ] Circular references causing infinite loops
- [ ] Missing state reset between operations

### Dead Code & Unreachable Paths
- [ ] Functions/methods never called
- [ ] Imports never used
- [ ] Conditions always true/false (e.g., if True, if 1)
- [ ] Code after return/throw/exit
- [ ] Feature flags always on/off
- [ ] Commented-out code that should be removed
- [ ] Unreachable except/switch cases

### API Usage
- [ ] Deprecated API usage (check against version risk profile)
- [ ] Incorrect parameter order
- [ ] Missing required parameters
- [ ] Wrong return type assumption
- [ ] API contract violation (wrong request shape, wrong response parsing)
- [ ] HTTP status code misinterpretation
- [ ] Missing retry/timeout on network calls
- [ ] Missing pagination handling on paginated APIs

### Typing & Contracts
- [ ] Type mismatch (string vs number, int vs float)
- [ ] Wrong interface implementation (missing methods, wrong signatures)
- [ ] Variance issues (covariant/contravariant misuse)
- [ ] Optional/nullable not handled (null reference risk)
- [ ] Union type not fully handled (missing branch)
- [ ] Generic type constraints violated

### Integration Issues
- [ ] Mismatched data formats between services
- [ ] Missing version compatibility checks between services
- [ ] Inconsistent error codes/messages between modules
- [ ] Circular dependencies between modules
- [ ] Missing retry/idempotency on integration calls
- [ ] Webhook/callback handlers missing signature verification

### React / Frontend Bugs (add to any React SPA audit)

- [ ] **`window.location` used for in-app route checks instead of `useLocation()`** — search for `window.location.pathname` or `window.location.href` used for route detection. In SPAs, `useLocation()` from react-router is reactive; `window.location` is not and causes stale checks after SPA navigation.
- [ ] **Loose equality (`==`) instead of strict (`===`)** — search for `==` in comparisons. Type coercion can cause unexpected matches (e.g., `"1" == 1`, `[1] == 1`). Check especially in route path comparisons and ID comparisons.
- [ ] **`JSON.parse(localStorage.getItem(...))` without try/catch** — search for `JSON.parse(localStorage`. Corrupted localStorage data throws an uncaught `SyntaxError`. Wrap in try/catch with a default value.
- [ ] **`parseInt()` without radix parameter** — search for `parseInt(` without `, 10)` or `, 2)` etc. While modern browsers default to base 10, legacy environments may interpret leading zeros as octal.
- [ ] **`useEffect` cleanup resets state that should persist** — check if cleanup functions reset auth state, form data, or other persistent state. Cleanup should cancel in-flight requests, not reset derived state.
- [ ] **`useEffect` with missing middle-case branches** — check effects with `if/if` (not `if/else if/else`) that don't cover all possible values of their dependency. Missing branches leave state unchanged from the previous value.
- [ ] **Mutable default parameters** — search for `function f(x = {})` or `function f(x = [])`. In JavaScript, default parameters are re-evaluated each call (unlike Python), but the pattern is still a code smell for confusion.
- [ ] **`window.open()` without `noopener,noreferrer` for external URLs** — search for `window.open(url, "_blank")` without third argument. The opened page gets `window.opener` reference (reverse tabnabbing). For blob URLs the risk is lower but the pattern should be consistent.
- [ ] **`dangerouslySetInnerHTML` or `innerHTML` with external data** — search for `innerHTML` and `dangerouslySetInnerHTML`. Even if the result is only read back (e.g., `div.innerHTML = text; return div.textContent`), the innerHTML assignment can trigger side effects with crafted payloads.
- [ ] **`window.location.assign()` or `window.location.replace()` for SPA navigation** — search for `window.location.assign(` and `window.location.replace(`. In SPAs, use `useNavigate()` from react-router. Full page reloads lose app state.
- [ ] **`target="_blank"` links without `rel="noopener noreferrer"`** — search for `target="_blank"` without `rel="noopener noreferrer"` on `<a>` tags. Reverse tabnabbing vulnerability.
- [ ] **`key={index}` in list renders causing stale state** — search for `key={index}` in `.map()` calls. When items are deleted from the middle, the last item's component gets the key of the deleted one, potentially showing stale state (e.g., checked checkboxes, expanded accordions).
- [ ] **Race condition: async effect without cancellation** — search for `useEffect` with `async` or `.then()` inside and no `AbortController`. If the component unmounts or deps change before the async call completes, the callback may set state on an unmounted component or overwrite newer data with stale results.
- [ ] **`useState` for derived data** — check if `useState` is used for values that can be computed from props or other state. This causes sync bugs when the source data changes but the derived state isn't updated.
- [ ] **Missing `useEffect` cleanup for subscriptions** — search for `addEventListener`, `setInterval`, `setTimeout`, `Observable.subscribe`, or WebSocket in `useEffect` without corresponding cleanup (`removeEventListener`, `clearInterval`, `clearTimeout`, `unsubscribe`, `close`).
- [ ] **`encodeURIComponent` mismatch with `window.location.pathname`** — `window.location.pathname` returns the URL-encoded path. Comparing it with a string that was `encodeURIComponent`'d may fail if the browser decodes the pathname. Use `useLocation().pathname` from react-router (decoded).
- [ ] **Hardcoded route strings instead of route constants** — search for `=== "/path"` or `=== "/path/"` in route checks. If routes change, all hardcoded checks break. Use route constants or `useMatch()`.

#### Django / DRF Bugs (add to any Django audit)

- [ ] **`transaction.rollback()` inside `with transaction.atomic()`** — search for `transaction.rollback()` in `except` blocks that follow `with transaction.atomic():`. The atomic context manager handles rollback automatically on exception; calling `rollback()` explicitly is a no-op (Django 4+) or raises `TransactionManagementError`. Remove the explicit rollback calls.
- [ ] **`== None` / `!= None` instead of `is None` / `is not None`** — search for `== None` and `!= None` across all Python files. PEP 8 mandates `is None` for identity checks. `== None` can trigger `__eq__` on model objects (causing unexpected DB queries) or return false positives if `__eq__` is overridden. Especially dangerous on deferred FK fields.
- [ ] **`datetime.now()` instead of `timezone.now()`** — search for `datetime.now()` in views, services, and utils. With `USE_TZ=True`, `datetime.now()` returns a naive datetime. Comparing naive with aware datetimes raises TypeError. Saving naive datetimes to DateTimeField causes Django to issue warnings and may silently interpret as UTC.
- [ ] **`strftime("%B")` for month name comparison** — search for `strftime("%B")` or `strftime("%b")` used with hardcoded month name lists. `%B` returns the month name in the server's locale, which may not match the hardcoded list (e.g., 'January' vs 'enero'). Use integer month (`.month`, 1-12) instead.
- [ ] **`.get(id=...)` without DoesNotExist handling** — search for `.get(id=...)` or `.get(pk=...)` outside try/except blocks. If the object doesn't exist, this raises `Model.DoesNotExist` (500 error). In multi-tenant apps, also check that the query is scoped to the tenant (e.g., `.get(id=id, id_church=church)`).
- [ ] **`.filter().first()` without None check** — search for `.filter(...).first()` followed by immediate attribute access (`.id`, `.name`, etc.) without a None guard. `.first()` returns None when no match exists; `None.id` raises AttributeError.
- [ ] **`data.pop("key")` without default** — search for `.pop("key")` (no second argument) on request data or dicts from user input. If the key is missing, raises KeyError. Use `.pop("key", None)` or `.get("key")` instead.
- [ ] **`int(field.get("key"))` without None guard** — search for `int(...get("key"))` or `int(...get("key", ...))` patterns. If the key is missing, `.get()` returns None, and `int(None)` raises TypeError. Use `int(field.get("key") or 0)` or check for None first.
- [ ] **`data.get("key")[0]` without empty/None check** — search for `.get("key")[0]` or `.get("key")[0].upper()`. If the key is missing, `.get()` returns None and `None[0]` raises TypeError. If the value is empty string, `""[0]` raises IndexError. Add a fallback: `(data.get("key") or "X")[0]`.
- [ ] **Signal handlers that catch Exception without re-raising** — search for `except Exception:` in signal handler functions (decorated with `@receiver` or `@post_save`/`@m2m_changed`). If the handler catches and logs but doesn't re-raise, the transaction commits with partial updates, leaving the database in an inconsistent state. Re-raise after logging, or use `transaction.set_rollback(True)`.
- [ ] **`print()` for error logging instead of `logger`** — search for `print(` in views, utils, services, and signals. `print()` bypasses Django's logging infrastructure — output goes to stdout, cannot be filtered by level, and is invisible in log aggregation. Replace with `logger.error()` / `logger.warning()`.
- [ ] **`except (SomeException, Exception):` redundant catch** — search for `except (..., Exception):` where Exception is the second or later type. Since `Exception` is the base class, the first type is redundant. This pattern often indicates confusion about exception hierarchy.
- [ ] **`except: pass` swallowing all errors** — search for `except:\n    pass` or `except Exception:\n    pass`. Bare `except:` catches `SystemExit` and `KeyboardInterrupt`. `except Exception: pass` hides all runtime errors. At minimum log the exception; better to catch specific exception types.
- [ ] **Duplicate key in dict literal** — search for dict literals where the same key appears twice. Python dicts allow duplicate keys in literals but the last one wins, making the first assignment dead code. Common in large response dicts built by hand.
- [ ] **`permission_classes` assigned twice in same class** — search for consecutive `permission_classes = [...]` lines. The second overwrites the first. Copy-paste error.
- [ ] **`fields = '__all__'` in serializers** — count occurrences. Each one exposes all model fields including audit timestamps, FK IDs, and potentially sensitive data. Prefer explicit field lists. The project's own conventions may explicitly ban `__all__`.
- [ ] **Inactive apps still routed in `urls.py`** — check if apps removed from `INSTALLED_APPS` still have `include()` entries in the root URL configuration. Routes are live but app infrastructure (signals, models, migrations) is not initialized.
- [ ] **Duplicate utility functions across modules** — check for the same utility function (e.g., `get_date`, `get_datetime`, `now`) defined in multiple modules. Bug fixes in one don't propagate. Consolidate into a canonical location.
- [ ] **`bulk_create` without `batch_size`** — search for `bulk_create(` without `batch_size=`. Without it, all INSERTs go in one query, risking PostgreSQL parameter limit errors for wide tables.
- [ ] **`.save()` without `update_fields` after initial save** — search for patterns where an object is saved, then a field is modified and saved again without `update_fields`. The second save writes all columns, potentially triggering signal handlers and storage backends unnecessarily. Use `save(update_fields=['field1', 'field2'])`.
- [ ] **N+1 query via re-fetch in serializer.data loop** — search for `for item in serializer.data:` followed by `.objects.get(id=item["id"])` or similar. The queryset instances are already available; iterate the queryset directly instead of re-fetching by ID.
- [ ] **`get_object_or_404` without tenant scoping** — search for `get_object_or_404(Model, id=...)` in multi-tenant apps. Must be `get_object_or_404(Model, id=id, id_church=church_instance)` to prevent cross-tenant access.
- [ ] **`church.objects.get(subdomain=get_origin(request))` without DoesNotExist** — search for this pattern. `get_origin(request)` can return None (no Origin/Referer header), and `get(subdomain=None)` raises DoesNotExist. Use `get_iglesia(request)` which handles the lookup properly.
- [ ] **`is_past_date` using locale-dependent month names** — check for functions that compare month names via `strftime("%B")` against a hardcoded list. Fails in non-matching locales. Use integer month comparison instead.
- [ ] **`upcoming_birthdays` only returns current month** — check birthday-reminder queries that filter by `month=today.month AND day__gte=today.day`. This misses birthdays in the next month. Use a proper date-range approach spanning month boundaries.

### Version-Specific Issues
- [ ] APIs deprecated or removed in the detected version (cross-ref Phase 4 risk profile)
- [ ] Known bugs in the exact version (check CVEs, issue trackers)
- [ ] Breaking changes between versions not handled
- [ ] Features used that don't exist in the detected version

---

## Security Checklist

### Authentication
- [ ] Weak password requirements / no password policy
- [ ] Missing rate limiting on auth endpoints
- [ ] Plaintext password storage (must be bcrypt/argon2/scrypt)
- [ ] Missing or weak password reset flow
- [ ] Multi-factor authentication not enforced for sensitive operations
- [ ] Session fixation vulnerability
- [ ] Missing account lockout after failed attempts
- [ ] Credentials in URLs or logs
- [ ] Default/placeholder credentials in code

### Authorization & Access Control
- [ ] Missing authorization checks on endpoints/handlers
- [ ] IDOR (Insecure Direct Object Reference) — user can access other users' data by ID
- [ ] Missing role/permission checks
- [ ] Privilege escalation paths (user → admin, horizontal escalation)
- [ ] Missing ownership verification before modify/delete
- [ ] Overly permissive CORS configuration
- [ ] Missing CSRF protection on state-changing operations
- [ ] JWT claims not validated (especially role/permissions)

### Input Validation & Injection
- [ ] SQL injection (string concatenation in queries, missing parameterized queries)
- [ ] NoSQL injection
- [ ] Command injection (user input in shell commands)
- [ ] Path traversal (user input in file paths, missing path normalization)
- [ ] XSS — reflected, stored, DOM-based (missing output encoding)
- [ ] Template injection (user input in template engine)
- [ ] SSRF (server-side request forgery — user-controlled URLs)
- [ ] XXE (XML external entity — missing disable of external entities)
- [ ] LDAP injection
- [ ] Missing input validation on all user-facing endpoints
- [ ] Missing input length/size limits
- [ ] Missing content-type validation on uploads
- [ ] Deserialization of untrusted data

### Secrets & Sensitive Data
- [ ] Hardcoded secrets (API keys, passwords, tokens) in source code
- [ ] Secrets in config files committed to repo (check .env, config.yml, etc.)
- [ ] Secrets in client-side code (exposed to browser)
- [ ] Missing .gitignore for sensitive files
- [ ] Secrets logged in error messages or debug output
- [ ] Sensitive data in URL parameters (logged by proxies/CDNs)
- [ ] Missing data encryption at rest (DB, files, backups)
- [ ] Missing encryption in transit (HTTP instead of HTTPS for internal calls)
- [ ] PII not anonymized in logs/analytics
- [ ] Error messages exposing internal details (stack traces, paths, versions)

### Session & Token Management
- [ ] Session tokens not rotated after login
- [ ] Session tokens not invalidated on logout
- [ ] Overly long session expiration
- [ ] JWT with weak signing algorithm (HS256 with shared secret, "alg: none")
- [ ] JWT not verifying expiration
- [ ] JWT secret too short or hardcoded
- [ ] Refresh tokens not rotated
- [ ] Missing token scope validation
- [ ] Cookies without Secure, HttpOnly, SameSite flags
- [ ] Session data stored in client-accessible storage (localStorage for sensitive data)

### Dependencies
- [ ] Known vulnerable dependencies (run npm audit, safety, pip-audit, cargo audit, etc.)
- [ ] Dependencies with no pinned versions (floating, latest)
- [ ] Unused dependencies (attack surface)
- [ ] Dependencies from untrusted sources (non-official registries)
- [ ] Missing dependency license check (license compliance)

### Configuration Security
- [ ] Debug mode / detailed errors enabled in production
- [ ] Missing security headers (CSP, X-Frame-Options, X-Content-Type-Options, HSTS)
- [ ] Insecure TLS configuration (old protocols, weak ciphers, missing cert validation)
- [ ] Missing rate limiting on all public endpoints
- [ ] File permissions too open (world-readable/writable)
- [ ] Container running as root
- [ ] Missing network segmentation / overly permissive firewall rules
- [ ] Admin interfaces exposed publicly without auth
- [ ] Missing request size limits
- [ ] Clickjacking protection missing (X-Frame-Options / CSP frame-ancestors)

### Cryptography
- [ ] Weak hashing (MD5, SHA1 for passwords or security-sensitive data)
- [ ] Weak random number generation (Math.random, random.random for security)
- [ ] Hardcoded IV/nonce for encryption
- [ ] ECB mode for block encryption
- [ ] Custom/rolled crypto instead of standard libraries
- [ ] Missing salt or static salt for hashing
- [ ] Key derivation not using PBKDF2/argon2/bcrypt

### Inter-Service Communication
- [ ] Missing mutual TLS between services
- [ ] Missing API key/token for internal service calls
- [ ] Internal services accessible without auth
- [ ] Missing request signing for webhook handlers
- [ ] Missing replay protection (timestamps, nonces)
- [ ] gRPC/GraphQL endpoints without auth/introspection disabled in prod

### Language/Framework Specific
- [ ] Python: pickle deserialization, yaml.load without SafeLoader, eval/exec, os.system
- [ ] Node.js: eval, child_process exec with user input, prototype pollution, require with user input
- [ ] Go: text/template HTML injection, unchecked type assertions, goroutine leak as DoS vector
- [ ] Java: deserialization gadgets, JNDI injection, SpEL injection, weak TrustManager
- [ ] PHP: file_get_contents with user URL, unserialize, eval, shell_exec, SQL injection patterns
- [ ] Ruby: eval, send, constantize, YAML.load, SQL string interpolation
- [ ] C#: Razor injection, ViewState issues, XML deserialization, Process.Start with user input
- [ ] Detect language/framework from Phase 2 and apply language-specific checks

#### React / Frontend Security (add to any React SPA audit)

- [ ] **JWT tokens in localStorage via Redux Persist** — check if `redux-persist` stores the session reducer (containing `token` and `refreshToken`) in `localStorage`. Any XSS vulnerability gives the attacker full access to long-lived refresh tokens. Prefer httpOnly cookies for refresh tokens, in-memory for access tokens.
- [ ] **WebSocket sends token in message payload** — check if `ws.send(JSON.stringify({ type: "auth", token }))` is used on WebSocket open. The token is visible in message payloads (server logs, ws:// dev traffic). Prefer `Sec-WebSocket-Protocol` header or query parameter on `wss://` URL.
- [ ] **`innerHTML` or `dangerouslySetInnerHTML` with external/API data** — search for `innerHTML` and `dangerouslySetInnerHTML`. Even if the result is only read back as text, the innerHTML assignment can trigger side effects (e.g., `<img onerror>` handlers). Use `document.createTextNode()` or a textarea-based entity decoder.
- [ ] **`window.open()` without `noopener,noreferrer` for external URLs** — search for `window.open(url, "_blank")` without third argument. The opened page can access `window.opener` and redirect the parent page (reverse tabnabbing).
- [ ] **`target="_blank"` links without `rel="noopener noreferrer"`** — search for `target="_blank"` on `<a>` tags without `rel="noopener noreferrer"`. Same reverse tabnabbing risk as `window.open()`.
- [ ] **Google Maps / third-party API keys in client-side code** — check for `useJsApiLoader({ googleMapsApiKey: ... })` or similar. While unavoidable for some JS APIs, ensure keys are restricted by HTTP referrer in the provider's console. Prefer backend proxy for sensitive operations (geocoding, etc.).
- [ ] **Sensitive data in URL parameters** — search for `?token=`, `?key=`, `?secret=`, `?api_key=` in client-side code. URL parameters are logged by proxies, CDNs, and analytics services.
- [ ] **`console.error` with full error details in production** — check if Vite/Rollup config drops `console` in production builds (`drop: ["console", "debugger"]`). If not, error details (stack traces, paths, component info) are exposed in browser DevTools.
- [ ] **`eval()` or `new Function()` with user input** — search for `eval(`, `new Function(`, `setTimeout(string)`, `setInterval(string)`. These execute arbitrary code in the user's browser.
- [ ] **`postMessage` without origin validation** — search for `window.addEventListener("message", ...)` without checking `event.origin`. Unvalidated postMessage handlers can receive messages from any origin.
- [ ] **Cross-tab sync reading persisted Redux state** — check if `useCrossTabSync` or similar parses `localStorage` data from `storage` events. This confirms the full session (including tokens) is serialized in localStorage. Mitigate by moving tokens to httpOnly cookies.
- [ ] **Unsafe `JSON.parse(localStorage.getItem(...))`** — search for `JSON.parse(localStorage`. Corrupted or malicious localStorage data throws an uncaught `SyntaxError`. Always wrap in try/catch.
- [ ] **`import.meta.env` variables exposed in client bundle** — check that `.env` variables prefixed with `VITE_` (or framework equivalent) don't contain secrets. All env vars in the client bundle are visible in browser DevTools.
- [ ] **Missing CSP headers** — check if the server sets `Content-Security-Policy` headers. Without CSP, XSS vulnerabilities are easier to exploit. CSP can mitigate injection even if other defenses fail.
- [ ] **`<a href={userInput}>` without validation** — search for `<a href={...}>` where the href comes from user input or API data. `javascript:` URLs in href attributes can execute arbitrary code. Validate or sanitize href values.

#### Django / DRF Security (multi-tenant focus)

- [ ] **`fields = '__all__'` in serializers** — especially on User model (exposes password hash, is_superuser, user_permissions). Check every serializer; ban `__all__` on models with PII or auth fields.
- [ ] **`traceback.print_exc()` in view exception handlers** — leaks stack traces (file paths, local variables, DB query fragments) to stdout/logs. Check for `str(e)` returned in Response bodies (bypasses ASGI traceback redaction).
- [ ] **`print(request.data)` / `print(request.POST)` / `print(body)` in views or middleware** — logs full request payloads including PII (identity docs, phones, addresses, photos) to stdout/container logs.
- [ ] **Missing tenant scoping on `.get(id=...)` / `get_object_or_404(Model, id=...)`** — in multi-tenant apps, every object fetch by user-supplied id must filter by tenant FK (e.g., `id_church=church_instance`). Search for unscoped `.get(id=...)` across all views and services.
- [ ] **Rate limiting disabled or empty** — check `DEFAULT_THROTTLE_CLASSES` and `DEFAULT_THROTTLE_RATES` in DRF settings. Empty lists = no rate limiting on any endpoint.
- [ ] **Predictable password generation from PII** — check `create_user()` / `set_password()` calls where password is derived from phone, birth date, document number, or other PII fields.
- [ ] **Captcha/Turnstile bypass gated to `settings.DEBUG`** — check if `condition_bypass=settings.DEBUG` is passed to captcha verification. This disables bot protection in any deployment with DEBUG=True.
- [ ] **Inactive apps still routed in `urls.py`** — check if apps removed from `INSTALLED_APPS` still have `include()` entries in the root URL configuration. Unmaintained views may have weaker security.
- [ ] **SSRF via dynamic proxy fetching** — check for `requests.get()` calls that fetch proxy lists from public APIs (proxyscrape, etc.) and route server-side requests through them. Also check for user-controlled URLs in `requests`/`urllib` calls.
- [ ] **`.values()` without field arguments** — returns all model columns as dicts, equivalent to `fields='__all__'` at runtime. Check for bare `.values()` on financial or PII-bearing models.
- [ ] **WebSocket accept-before-auth** — check if `await self.accept()` is called before authentication in Channels consumers. Unauthenticated connections can be held open (DoS vector).
- [ ] **JWT access token not checked against blacklist for WebSocket** — SimpleJWT's `AccessToken()` validates signature/expiry but not blacklist. Check if WS auth path verifies token against blacklist or checks user active status.
- [ ] **Superuser bypass of tenant/module gating without audit logging** — check if `is_superuser` skips subscription/module checks and resolves tenant from client-controlled Origin header. Cross-tenant superuser access should be audited.
- [ ] **CORS regex allowing any subdomain** — check `CORS_ALLOWED_ORIGIN_REGEXES` for patterns like `r'^https://[\\w-]+\\.example\\.com$'` that trust any subdomain without validation against a database.
- [ ] **Stale settings files in repo** — check for `settings.py.old`, `settings_local.py`, or other backup config files that may contain outdated or insecure configuration.
- [ ] **`AllowAny` public endpoints returning full model serializers** — check every `permission_classes = [AllowAny]` view for what data it returns. Public endpoints should return minimal public fields only.
- [ ] **`AllowAny` logout endpoint** — verify it doesn't require a valid token (user may have expired token at logout time). Acceptable pattern.
- [ ] **`AllowAny` subdomain/tenant existence check** — check if a public endpoint reveals whether a subdomain exists (enumeration risk). Low severity but worth noting.
- [ ] **Username/email enumeration in login** — check if login endpoint has separate code paths for "user exists" vs "user does not exist" (different DB queries, different response timing, different status codes).