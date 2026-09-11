# Critical Comment Detection Guide

When deciding whether to preserve or remove an existing comment, use this guide. This is especially important in full regeneration mode.

## Preserve (indispensable comments)

These comments encode knowledge that cannot be reconstructed from the code. Removing them loses institutional knowledge.

### Design decisions
```python
# We use a connection pool of 10 instead of 5 because benchmarking
# showed P99 latency drops 40% under burst traffic with this size.
```

### Why-not comments (explaining what ISN'T done and why)
```javascript
// We intentionally do NOT cache this endpoint because the upstream
# service has a 2s SLA and caching would mask outages.
```

### Race conditions / concurrency warnings
```rust
// WARNING: This must be called while holding the lock. Calling without
// the lock causes a data race on `shared_state`.
```

### Security notes
```java
// Do not log the full token. We truncate to first 8 chars to avoid
// leaking credentials in error reports sent to Sentry.
```

### Performance constraints
```go
// This loop is O(n^2) but n is always < 50 per the SLA contract.
// Do not optimize with a hash map — the constant factor is worse
// for small n and we measured a 3% throughput regression.
```

### Workarounds for external bugs
```python
# HACK: Pandas 2.1.0 has a bug where .loc with a boolean Series
# silently drops rows. Fixed in 2.1.2 but we can't upgrade yet.
# See https://github.com/pandas-dev/pandas/issues/12345
```

### TODO/FIXME with rationale
```javascript
// TODO(v2): Replace this manual retry with the framework's built-in
// retry policy once we migrate to framework v3. The manual retry
// exists because v2's retry doesn't support exponential backoff.
```

### Non-obvious business rules
```php
// Tax exemption only applies to non-profit organizations registered
// in the US. International non-profits are NOT exempt per legal review
// (see ticket LEGAL-2023-087).
```

### API stability / deprecation notices
```typescript
// @deprecated This endpoint will be removed in v3. Use /api/v2/users
// instead. Kept for backward compatibility with clients < v1.5.
```

### Platform-specific behavior
```go
// On Windows, this path uses backslashes. We normalize here because
// the config file format requires forward slashes regardless of OS.
```

## Remove (dispensable comments)

These comments add no value beyond what the code already says. Safe to remove in both modes (incremental and full regen).

### Restating the code
```python
# increment i by 1
i += 1

# set the result to the sum
result = a + b
```

### Obvious labels
```javascript
// constructor
function Foo() { ... }

// returns the user
return user;
```

### Tautological docstrings
```python
def get_name(self):
    """Get the name."""
    return self.name
```

### Commented-out code
```python
# old_result = old_function(data)
# result = new_function(data)
result = process(data)
```

### Section dividers with no information
```javascript
// =============================
// =========== UTILS ===========
// =============================
```
(Exception: if the project consistently uses section dividers as a style convention, keep them.)

### TODO with no context
```python
# TODO: fix this
```
(If the TODO has rationale like the example above, preserve it.)

## Judgment call (case-by-case)

These require reading the surrounding code to decide:

### Docstrings that only restate the function name
```python
def validate_email(email):
    """Validate email."""
```
→ Remove the tautological part, but consider adding real content about validation rules.

### Comments explaining "what" in complex code
```python
# Binary search for the insertion point
idx = bisect_left(sorted_list, value)
```
→ For well-known algorithms, this is redundant. For project-specific algorithms, expand it to explain the approach.

### TODO comments with dates
```python
# TODO(2024-01-15): remove this after migration
```
→ If the date has passed and the code still uses the old pattern, the TODO is stale — investigate whether the migration is still planned or was completed and this was forgotten.

### License headers
→ Always preserve. These are legal requirements, not documentation.

### Type coercion explanations
```javascript
// Convert to number because the API returns string
const num = Number(str);
```
→ This adds context (why the conversion is needed). Preserve unless the function already documents that it returns a string.