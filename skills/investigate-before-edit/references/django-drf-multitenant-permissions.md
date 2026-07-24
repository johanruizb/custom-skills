# Django + DRF Multi-Tenant Permission Patterns

> Reference for IglesiaApp's custom permission system. Key patterns discovered during the permisos-redesign implementation.

## Middleware Ordering

- Django's `AuthenticationMiddleware` sets `request.user` (session-based) in `process_request`.
- DRF's JWT/token authentication runs LATER, inside `APIView.dispatch`.
- Custom middleware in `process_request` sees `AnonymousUser` for JWT users.
- **Fix:** Don't gate access in `process_request` middleware. Let DRF permission classes do the real check. The middleware should only set context (like `_effective_permissions`), not return 403.

## HasPermission Class

- Custom DRF permission class that checks `require_permission("modulo.recurso.accion")` on views.
- Uses `_effective_permissions` set by middleware, with fallback to resolver.
- For superusers: resolver returns `ALL_PERMISSIONS` (all catalog entries).
- For pastors (group 13): resolver returns `ALL_PERMISSIONS` (same as superuser, own church).
- For secretaria_general (group 15): resolver returns `ALL_PERMISSIONS` minus finanzas permissions.
- **Important:** Overrides (grant/revoke) must be applied AFTER the role-based ALL_PERMISSIONS shortcut, not before. The resolver was returning early for pastor/secretaria without applying overrides.

## Tenant Isolation

- Every query filters by `id_church` (or `_church_context` from middleware).
- Records with `id_church=None` are global — they won't be found by tenant-scoped queries.
- When migrating global records to a new system, they must be replicated to every tenant.
- 404 can mean "this record doesn't belong to this tenant" not "this record doesn't exist."

## Migration Patterns

- Use `get_or_create` for idempotent migrations.
- After migration, query the database to verify counts per tenant.
- Check edge cases: global records, null foreign keys, pre-existing records.
- Run migration twice to verify idempotency.

## Permission Mapping

- Legacy Django Groups → new ChurchRole with `category` from `positions_per_group` name.
- Legacy Django permissions (e.g., `personas.add_person`) → new catalog permissions (e.g., `personas.miembros.crear`).
- Mapping file: `backend/permisos/management/commands/permission_mapping.py` — a dict of `{old_codename: new_permission_key}`.
- System roles (superuser, pastor, secretaria_general) are created by `create_system_roles` command.
- Legacy roles are migrated by `migrate_legacy_roles` command.
