# Django / DRF Performance Anti-Patterns

Concrete patterns, search queries, and evidence from real audits. Use alongside the analysis checklists.

## Search Queries (ripgrep/grep)

### Pagination
```
# No pagination at all
rg "DEFAULT_PAGINATION_CLASS\|PAGE_SIZE\|pagination_class" --include "*.py"
# Explicitly disabled pagination
rg "pagination_class\s*=\s*None" --include "*.py"
```

### Caching
```
# No CACHES config
rg "CACHES\s*=" --include "*.py" --include "*.conf"
# No cache usage
rg "cache\.get\|cache\.set\|@cache_page\|from django\.core\.cache" --include "*.py"
```

### Serializer over-fetching
```
# fields = '__all__' count
rg "fields\s*=\s*['\"]__all__['\"]" --include "*.py" | wc -l
# Bare .values() (returns all columns)
rg "\.values\(\s*\)" --include "*.py"
```

### N+1 queries
```
# Loop over serializer.data + re-fetch
rg "for .* in .*serializer\.data" --include "*.py" -A 5
# .count() inside for loop
rg -U "for .* in .*:\n.*\.count\(\)" --include "*.py"
# .filter() inside for loop (likely N+1)
rg -U "for .* in .*:\n.*\.filter\(" --include "*.py"
# .all() inside for loop (likely N+1)
rg -U "for .* in .*:\n.*\.all\(\)" --include "*.py"
```

### Bulk operations
```
# .save() in loop (should be bulk_update)
rg -U "for .* in .*:\n.*\.save\(\)" --include "*.py"
# .create() in loop (should be bulk_create)
rg -U "for .* in .*:\n.*\.create\(" --include "*.py"
# bulk_create without batch_size
rg "bulk_create\([^)]*\)" --include "*.py" | rg -v "batch_size"
```

### Synchronous HTTP in request path
```
# requests.get/post in views
rg "requests\.\(get\|post\)" --include "*.py" backend/views.py
# requests calls without timeout
rg "requests\.\(get\|post\)\([^)]*\)" --include "*.py" | rg -v "timeout"
```

### Missing select_related / prefetch_related
```
# FK access in loop without select_related
rg -U "for .* in .*:\n.*\.id_person\." --include "*.py"
# M2M access in loop without prefetch_related
rg -U "for .* in .*:\n.*\.all\(\)" --include "*.py" | rg "\.all\(\)"
```

### Missing .only() / .defer()
```
# Count .only() usage
rg "\.only\(" --include "*.py" | wc -l
# Count .defer() usage
rg "\.defer\(" --include "*.py" | wc -l
```

### Debug prints
```
# print() in view files
rg "print\(" --include "*.py" backend/views.py
```

### Missing indexes
```
# Count models with explicit indexes
rg "class Meta:" --include "*.py" -A 10 | rg "indexes"
# Count id_church FK fields (for multi-tenant)
rg "id_church\s*=" --include "*.py" | wc -l
```

### Connection pool
```
# conn_max_age in DATABASES
rg "conn_max_age\|CONN_MAX_AGE" --include "*.py"
```

## Common Django/DRF Performance Findings

### 1. Unbounded List Endpoints
**Pattern:** `ModelViewSet` or `ListAPIView` without `pagination_class` and no global `DEFAULT_PAGINATION_CLASS`.
**Evidence:** `REST_FRAMEWORK` settings dict lacks `DEFAULT_PAGINATION_CLASS` and `PAGE_SIZE`.
**Fix:** Add global pagination or per-view pagination.
**Risk:** Low. Frontend may need to handle paginated response format.

### 2. N+1 via Serializer Loop
**Pattern:** Serialize queryset, then iterate `serializer.data` and re-fetch related objects per item.
```python
serializer = MySerializer(queryset, many=True)
for item in serializer.data:
    related = RelatedModel.objects.get(id=item['id'])  # N+1!
```
**Fix:** Prefetch before serialization, or batch-fetch after.
**Risk:** Low.

### 3. N+1 via Recursive Tree Traversal
**Pattern:** Recursive function that calls `.filter(parent=X)` or `.children.filter()` per node.
```python
def build_tree(node):
    children = node.children.filter(is_active=True)  # Query per node!
    for child in children:
        build_tree(child)
```
**Fix:** Fetch all nodes in one query, build tree in memory with dict keyed by parent_id.
**Risk:** Medium — tree structure must match.

### 4. N+1 Count Queries
**Pattern:** Loop over groups and call `.count()` per group.
```python
for group in groups:
    count = person_group.objects.filter(id_group_church=group).count()  # COUNT per group
```
**Fix:** `groups.annotate(person_count=Count('id_group_church_in_person'))`
**Risk:** Low.

### 5. Loop with .save() Instead of bulk_update
**Pattern:** Iterate queryset, modify fields, call `.save()` per instance.
```python
for instance in instances:
    instance.field = new_value
    instance.save()  # UPDATE per instance
```
**Fix:** `bulk_update(instances, fields=['field'])`
**Risk:** Low. `bulk_update` does not call `save()` (no signals, no auto_now).

### 6. Synchronous External HTTP in Request Path
**Pattern:** `requests.get()` or `requests.post()` called from a view or view-adjacent service.
**Evidence:** Found in auth (Turnstile verification), geocoding, Bible verse proxy, email sending.
**Fix:** Add timeout, cache results, or move to async task queue.
**Risk:** Medium — changing sync to async may require infrastructure changes.

### 7. Missing Composite Indexes in Multi-Tenant Apps
**Pattern:** All queries filter by `id_church` but no composite indexes on `(id_church, status)`, `(id_church, deleted)`, etc.
**Evidence:** `Meta.indexes` is empty or absent on most models.
**Fix:** Add composite indexes for common filter combinations.
**Risk:** Medium — requires migration, may affect write performance.

### 8. fields='__all__' on Wide Models
**Pattern:** Serializer uses `fields = '__all__'` on a model with 20+ fields including large text, audit timestamps, and sensitive data.
**Evidence:** Count of `fields = '__all__'` across all serializers.
**Fix:** Replace with explicit field list. Create separate serializers for list vs detail views.
**Risk:** Low — but verify frontend receives all needed fields.

## Django Settings Checklist

```python
# Required for production:
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

DATABASES = {
    'default': {
        # ...
        'CONN_MAX_AGE': 60,  # Lower than default 600 for ASGI
        'CONN_HEALTH_CHECKS': True,
    }
}
```
