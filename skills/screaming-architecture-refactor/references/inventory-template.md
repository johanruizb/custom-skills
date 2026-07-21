# Inventory Template

Used by Step 6 of the screaming-architecture-refactor skill. Every file under `TARGET_PATH` must appear in this inventory, including dotfiles, test files, configs, assets, and docs.

## Format

One row per file, in this exact column order:

```
| source (relative to PROJECT_ROOT) | capability | role | language | responsibility (<=120 chars) | shared? | ambiguous? |
```

## Columns

- **source** — path relative to `PROJECT_ROOT`, using forward slashes.
- **capability** — the domain/capability the file serves (`auth`, `billing`, `reports`, `shared`, `?` if unresolved).
- **role** — one of: `component`, `service`, `model`, `schema`, `hook`, `type`, `validation`, `test`, `util`, `asset`, `config`, `doc`, `barrel`, `entrypoint`, `story`, `fixture`, `other`.
- **language** — `ts`, `tsx`, `js`, `jsx`, `py`, `rs`, `go`, `json`, `yaml`, `md`, `css`, `html`, `sql`, `other`.
- **responsibility** — one-line description of what the file actually does, based on its content (not its name).
- **shared?** — `yes` only if the file is used by 2+ distinct capabilities; otherwise `no`.
- **ambiguous?** — `yes` if classification is uncertain and needs resolution before Step 5; otherwise `no`.

## Example

```
| src/components/UserMenu.tsx                 | auth     | component  | tsx | Dropdown showing user info + logout button           | no  | no  |
| src/services/tokenRefresh.ts                | auth     | service    | ts  | Silently refreshes JWT before expiry                 | yes | no  |
| src/utils/formatDate.ts                     | shared   | util       | ts  | Locale-aware date formatting used by 4 features      | yes | no  |
| src/components/Header.tsx                   | ?        | component  | tsx | Site header; imports from auth, billing, and reports | no  | yes |
```

## Rules

- Do not omit any file. If the inventory row count != `find <TARGET_PATH> -type f | wc -l`, the scan is incomplete.
- Dotfiles (`.eslintrc`, `.storybook/config.js`, `.env.example`, `.gitkeep`) are included.
- Generated files (build output, `.next/`, `dist/`, `__pycache__/`) are listed with role `other` and responsibility `generated — do not move` so they are explicitly excluded from the move map rather than silently ignored.
- Ambiguous files must be resolved (read more content, trace imports) before Step 5. A file may not enter the move map with `ambiguous? = yes`.