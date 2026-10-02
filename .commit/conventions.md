# Commit conventions

Seeded on the first git-commit run, 2026-10-01.

## Gotchas

- No changelog at the root (`CHANGELOG*`, `CHANGES*`, `HISTORY*` all absent):
  commits write no changelog entry until one appears. When one is added, the
  skill's stale check re-fires and `config.json` gains a `changelog` field.