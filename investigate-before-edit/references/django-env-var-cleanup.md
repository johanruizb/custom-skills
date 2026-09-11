# Django Env Var Cleanup Pattern

## When to Use

When the user asks to clean up `.env.example`, remove dead env vars, consolidate redundant vars, or simplify Docker Compose / settings config.

## Investigation Steps

### 1. Find all consumed env vars

Grep for `config(` calls across the entire backend:

```bash
grep -rn 'config("' backend/ --include='*.py' | grep -oP 'config\("\K[^"]+' | sort -u
```

This is the **source of truth** — only these vars are actually consumed at runtime.

### 2. Compare with `.env.example`

Read `.env.example` and cross-reference against the consumed list. Every var in `.env.example` that is NOT in the consumed list is dead and should be removed.

### 3. Check Docker Compose files

Check `docker-compose.yml` and `docker-compose.test.yml` for env var references:

```bash
grep -n '\${.*}' docker-compose*.yml
```

If a compose file references a var that's no longer consumed, either:
- Remove the reference and hardcode the value (for local dev)
- Keep the reference if it's genuinely configurable per-deployment

### 4. Check helper scripts

Check `database/db.sh`, `start.sh`, `deploy.sh`, etc. for references to removed vars.

### 5. Check settings files

Check each settings file (`development.py`, `production.py`, `test.py`, `base.py`) for `config()` calls that reference the vars being cleaned up.

## Rules

### `.env.example`
- Must contain **every** var consumed by `config()` calls, with a sensible default or placeholder
- Must NOT contain vars that are no longer consumed
- Must NOT contain vars that are hardcoded in docker-compose.yml (they're not configurable)
- Must NOT contain vars that have sensible defaults in settings (they're optional)

### `docker-compose.yml` (local dev)
- Should be self-contained — use fixed values, not env-dependent
- `postgres` service: fixed user/password/db matching settings defaults
- No `postgres-test` service — test DB belongs in `docker-compose.test.yml`

### `docker-compose.test.yml`
- Can reference env vars if they differ from defaults (e.g., `postgres` hostname inside Docker vs `localhost` outside)
- But the compose file itself should have the correct values hardcoded

### Settings files
- `development.py`: can have defaults for convenience (local dev should work without `.env`)
- `production.py`: NO defaults for required vars — missing env var should fail loudly
- `test.py`: defaults are fine (test settings are not production)

### `db.sh`
- Defaults must match `docker-compose.yml` values
- Should NOT read `LOCAL_DB_*` vars from `.env` — those are dead
- Should use fixed defaults: `iglesiaapp` / `postgres` / `postgres`

## Common Pitfalls

1. **Removing a var that's still consumed.** Always grep for `config("VAR_NAME")` before removing. A var in `.env.example` may look dead but be consumed in a settings file you didn't check.

2. **Adding defaults to production settings.** Production should fail on missing required vars. A default masks the error and the app starts with wrong config.

3. **Keeping redundant vars.** `DATABASE_URL_DEV` + `DATABASE_URL_PROD` → single `DATABASE_URL`. The env file (`DJANGO_ENV`) already determines which settings file loads.

4. **Forgetting `db.sh`.** The backup/restore script has its own defaults that must match docker-compose.yml.

5. **Forgetting `.gitignore`.** If `.gitignore` has `.env*`, it also ignores `.env.example`. Add `!.env.example` as an exception.
