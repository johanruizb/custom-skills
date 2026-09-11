# Move Map Schema

Used by Step 6 of the screaming-architecture-refactor skill. The move map is the machine-checkable contract between `analyze` and `apply`. Every row must be verifiable.

## Format

A Markdown table followed by a per-row detail block. The table is for quick scanning; the detail block holds the import rewrites and evidence.

### Table

```
| # | source (rel to PROJECT_ROOT) | destination (rel to PROJECT_ROOT) | kind | external_refs? |
```

- **kind** — `move`, `merge` (destination already exists, append content), `delete`, `stay`.
- **external_refs?** — `yes` if any file outside `TARGET_PATH` imports/references this file; `no` otherwise.

### Detail block (one per row)

```
## Row N — <source>

kind: move | merge | delete | stay
destination: <path or "—" for delete/stay>
evidence: <why this is the correct destination, or why delete/stay is justified>
import_rewrites:
  - file: <path of the file whose import must change>
    find: <old import string or path segment>
    replace: <new import string or path segment>
  - file: ...
barrel_updates:
  - barrel: <barrel file path>
    action: add-export | remove-export | update-path
    detail: <e.g. "add export { UserMenu } from ./UserMenu">
config_updates:
  - file: <config file path, e.g. tsconfig.json>
    change: <e.g. "path alias @/components/* -> @/features/*/components/*">
```

## Rules

- Every `source` must exist on disk at `analyze` time.
- Every `destination` must not exist (unless `kind: merge`).
- `kind: delete` requires `evidence` to cite either (a) the duplicate file with a content hash or diff, (b) the generator that produces it, or (c) the reference search that returned zero hits.
- `kind: stay` requires `evidence` to cite the constraint (framework-imposed location, build config that must sit at a fixed path, etc.).
- `import_rewrites` must cover every consumer found in Step 3's reference graph — both inside and outside `TARGET_PATH`.
- `barrel_updates` and `config_updates` are optional sections; include them only when the row triggers a barrel or config change.
- A row with `external_refs? = yes` must have at least one `import_rewrites` entry for a file outside `TARGET_PATH`.

## Sanity check (run before finishing Step 6)

```
for each row:
  assert exists(source) or kind == "stay"  # stay rows may already be at destination
  if kind == "move": assert not exists(destination)
  if kind == "delete": assert evidence != ""
  if kind == "stay": assert evidence != ""
  if external_refs == "yes": assert len(import_rewrites) >= 1
```

If any assertion fails, fix the plan before writing the artifact.