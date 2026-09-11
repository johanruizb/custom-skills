---
name: screaming-architecture-refactor
description: "Use when reorganizing a specific subpath of a project to Screaming Architecture + feature-based folders. Receives project root, target path, and mode (analyze | apply | verify). Designed to run repeatedly over different paths of the same project for incremental, consistent, safe migration."
license: MIT
metadata:
  author: Hermes Agent
  version: "1.1.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [architecture, refactoring, screaming-architecture, feature-folders, restructuring, imports, migration]
    related_skills: []
---

# Screaming Architecture Refactor

Reorganize a specific subpath of a project so that top-level directories express system capabilities (Screaming Architecture) and each feature folder collocates its own components, services, models, hooks, types, validations, tests, assets, and utils. Idempotent and incremental: designed to run over different paths of the same project across multiple sessions without undoing previous decisions.

## When to Use

- User asks to "reorganize", "restructure", "migrate to feature folders", or "apply screaming architecture" to a specific directory.
- A subpath mixes technical-layer folders (`components/`, `services/`, `hooks/`, `utils/`) that should be split by capability instead.
- User wants a safe, reviewed migration with full import/barrel/alias updates and validation, not a blind move.
- Incremental migration: user is converting a project folder-by-folder and wants each run to respect prior runs.

Don't use for:
- Whole-codebase greenfield scaffolding — scope that as a separate planning task first.
- Single-file moves or renames with no architectural intent.
- Framework-imposed layouts that cannot be changed (e.g. Next.js `app/` routes, Django app internals) unless the user explicitly wants to override them.

## Inputs

The skill always operates with three inputs. If any is missing, ask the user before proceeding:

- `PROJECT_ROOT` — absolute path to the project root (where config files, tsconfig, package.json, pyproject, etc. live).
- `TARGET_PATH` — absolute or project-relative path to the directory to reorganize. Must be inside `PROJECT_ROOT`.
- `MODE` — one of `analyze`, `apply`, `verify`.

`MODE` semantics:

| Mode | What happens | Mutates files? |
|------|--------------|----------------|
| `analyze` | Full scan + classification + proposed tree + move map. Writes the plan to disk only. | No (only writes the plan artifact) |
| `apply` | Executes the plan from `analyze` (or a prior plan artifact if present): moves files, updates imports/exports/aliases/config, then runs validations. | Yes |
| `verify` | Re-runs validations and checks for leftover files, broken references, empty dirs, and stale plan artifacts. No new moves. | No |

Recommended flow on a fresh path: `analyze` → user reviews → `apply` → `verify`. On a path already migrated by a prior run, jump straight to `verify` to confirm integrity, or `analyze` again to extend the migration.

## Plan Artifact

Every `analyze` run writes a plan to `<PROJECT_ROOT>/.hermes/screaming-arch/<sanitized-target-path>.md` (create the dir if missing). `apply` and `verify` read this artifact. If `apply` is invoked without a fresh artifact, first run `analyze` implicitly.

The artifact contains, in this exact order:

1. **Analysis summary** — one paragraph per identified capability/domain.
2. **Source inventory** — every file under `TARGET_PATH` (including hidden), with its real responsibility, language, and current location. Use the template in `references/inventory-template.md`.
3. **Target tree** — the proposed directory structure.
4. **Move map** — every `source → destination` pair, plus the import-rewrite rule for each. Use the schema in `references/move-map-schema.md`.
5. **Stays-in-place list** — files that cannot be moved and why (framework constraints, build config that must sit at a fixed location, etc.).
6. **Deletions list** — files proposed for deletion, each with evidence (duplicate, generated, obsolete).
7. **Import-rewrite plan** — which files outside `TARGET_PATH` need their imports updated, grouped by file.
8. **Risks** — ordered by severity.

## Procedure

Follow the steps in order. Each step lists its completion criterion — do not advance until it is met.

### Step 1 — Scan recursively, including hidden files

Scan every entry under `TARGET_PATH`, including dotfiles, test files, configs, assets, docs, and build output that lives alongside source.

```
find <TARGET_PATH> -type f
```

Then enumerate directories with a glob/find capability, e.g. `find <TARGET_PATH> -type d`. Include hidden directories (`.git` is excluded automatically if it is the project's git dir; other hidden dirs like `.storybook`, `.vscode`, `__mocks__`, `__snapshots__` are in scope).

Completion criterion: the file count you collected equals the count reported by `find <TARGET_PATH> -type f | wc -l`. If they differ, rescan the gap before continuing.

### Step 2 — Classify by real responsibility

For every file, determine what it actually does — not what its name suggests. Read enough of each file to identify:

- The capability/domain it serves (auth, billing, reports, onboarding, etc.).
- Its role within that capability (component, service, model/schema, hook, type, validation, test, util, asset, config, doc, barrel).
- Whether it is genuinely shared across multiple capabilities or belongs to exactly one.

**Batch-scan strategy for large directories (50+ files):** Do NOT read files one at a time. Instead, use a two-pass approach:

1. **Pass 1 — Gather metadata in bulk.** Use the code-runner capability to run a short script that reads the first ~60 lines + imports/exports of every file in one batch. Store results in a JSON file. This gives you the head (first meaningful lines), exports list, and import list for every file in a single tool call.
2. **Pass 2 — Classify from the metadata.** Iterate over the stored metadata and assign capability + role to each file. Only re-read a file individually when the head + exports are insufficient to classify.

This approach handles 196 files in ~2 tool calls instead of 196. Read more only when classification is ambiguous. See `references/batch-scan-strategy.md` for the full two-pass procedure with example code.

**Handling AGENTS.md / SECURITY.md / collocated docs:** These are documentation files that describe a capability folder. They are NOT stays-in-place — they move with their capability folder as collocated docs. Classify them as `meta` capability, `doc` role. In the move map, they move alongside the code they document.

Completion criterion: every file in the inventory has a `capability` and `role` assigned. Ambiguous files are flagged with `?` and resolved before Step 5.

### Step 3 — Trace imports, exports, aliases, references

Build the reference graph for `TARGET_PATH`:

- Internal imports within `TARGET_PATH` (who imports whom).
- Imports from `TARGET_PATH` coming from outside it (use a content search (glob/grep) with the target path as a pattern, e.g. `from ['"](\.\./)*<target-dir-name>` for JS, `from <target-dir>` for Python, etc.).
- Barrel files (`index.ts/js`, `__init__.py`, `mod.rs`) and what they re-export.
- Path aliases (`tsconfig.json` paths, `jsconfig.json`, `vite.config` alias, `webpack.resolve.alias`, `babel-plugin-module-resolver`, `pylint`/`mypy` path config, Django `INSTALLED_APPS`, etc.).
- Dynamic imports, lazy imports, and string-based references (e.g. `lazy(() => import("..."))`, `django.apps.get_model("app.Model")`, reflect-style lookups). Grep for `import(`, `require(`, `get_model`, `resolve`, and string literals that look like paths.

Completion criterion: for every file in `TARGET_PATH`, you know (a) who imports it and (b) what it imports. The outside-in list (files outside `TARGET_PATH` that reference inside) is non-empty only if real cross-boundary references exist — confirm by running a content search for the target's old path segments across `PROJECT_ROOT`.

### Step 4 — Identify capabilities and shared elements

Group files by the capability they serve. A capability is a coherent slice of business value the system offers (auth, checkout, reporting, member management, audit log, etc.). Files serving more than one capability are candidates for a `shared/` (or `common/`, `platform/`) folder — but only if they are genuinely cross-cutting. A file used by two features that are themselves part of the same capability does not qualify as shared.

Completion criterion: every file is assigned to exactly one capability or to `shared`. No file is left in a "misc" bucket; if you are tempted to create one, re-classify.

### Step 5 — Propose the target tree

Design the target structure so that:

- Top-level directories under `TARGET_PATH` represent capabilities (e.g. `auth/`, `billing/`, `reports/`), not technical layers.
- Each capability folder collocates its own `components/`, `services/`, `models/`, `hooks/`, `types/`, `validations/`, `tests/`, `utils/`, `assets/`, `docs/` — but only the subfolders that feature actually uses. Do not create empty subfolders for symmetry.
- A single `shared/` folder holds only genuinely cross-cutting elements. Avoid global `components/`, `services/`, `hooks/`, `utils/` at the root of `TARGET_PATH` unless every entry in them is truly shared.
- Tests live next to the code they test (collocated), unless the project's test runner requires a separate `__tests__/` or `tests/` dir — in that case, mirror the feature structure inside it.
- Hidden config dirs that must stay where they are (e.g. `.storybook`, `.vscode`) are listed in the stays-in-place section with a reason.

If a previous run already established a capability layout under a sibling path, reuse the same capability names and folder conventions. Do not invent parallel vocabularies.

Completion criterion: the target tree has no orphan technical-layer folder at its root, every leaf maps to at least one source file, and every source file maps to exactly one target leaf.

### Step 6 — Generate inventory, tree, and move map

Write the plan artifact (see the Plan Artifact section above) using the templates in `references/inventory-template.md` and `references/move-map-schema.md`. The move map must be machine-checkable: each row has `source`, `destination`, `import_rewrites` (list of `{file, find, replace}`), and `evidence` (why the move is correct).

For deletions, each row must cite the evidence: which file it duplicates (with a content hash or diff), or which generator produced it, or which import graph proves it is unreachable.

Completion criterion: the artifact is written to disk, and a quick sanity check passes — for every `source` in the move map, `os.path.exists(source)` is true; for every `destination`, no file exists yet (or the plan explicitly marks it as a merge).

### Step 7 — `analyze` mode: stop here

In `analyze` mode, present the artifact path to the user and a concise summary (capabilities found, file count, move count, deletion count, risks). Do not modify any project file other than the artifact. Wait for the user to review and either approve, request changes, or switch to `apply`.

Completion criterion: the user has acknowledged the plan (explicit approval, or a follow-up instruction to `apply`).

### Step 8 — `apply` mode: execute the moves

Execute the plan in this order to minimize broken intermediate states:

1. Create target directories (including hidden ones that are being moved, not the ones staying).
2. Move files with `git mv` when inside a git repo (preserves history); fall back to `mv` otherwise. Move one file at a time and verify each move succeeded before continuing — batch only when the destination parent already exists. For a source in a subfolder, take the destination filename from the source basename (`os.path.basename(src)` or `parts[-1]`), never from an intermediate subfolder name.
3. After all moves, update every import/export/barrel/alias listed in the move map. Use targeted edits; never rewrite a whole file just to change an import path. Preserve the original import's extension pattern, point barrel imports at the directory rather than the index file, and follow `references/import-rewrite-algorithm.md` for the exact logic.
4. Update config files that encode path aliases or module resolution (`tsconfig.json`, `jsconfig.json`, `vite.config.*`, `webpack.config.*`, `babel.config.*`, `pyproject.toml`, `setup.cfg`, `manage.py`/`INSTALLED_APPS`, `jest.config.*`, `tsconfig.spec.json`, etc.). Only touch the entries that reference `TARGET_PATH` or its old subpaths.
5. Delete files marked for deletion in the plan. Each deletion must have evidence recorded in the artifact; if evidence is missing or weak, skip the deletion and flag it in the final report instead.
6. Remove now-empty source directories. Verify each is empty before removing (`find <dir> -mindepth 1 -maxdepth 1 | wc -l` must be 0). Never remove a dir that still has content.

Do not change business logic. Do not reformat code. Do not rename identifiers. Only paths and import statements change.

Completion criterion: `find <TARGET_PATH> -type f` returns only the files listed in the stays-in-place section (or nothing, if nothing had to stay). Every move-map row is marked done. No empty directory remains under `TARGET_PATH`.

### Step 9 — Update external references

For every file outside `TARGET_PATH` that imported from it, apply the same import rewrites. This is the step most likely to be skipped — guard against it explicitly:

```
grep -rn "<old-path-segment>" <PROJECT_ROOT>
```

Run this for every old path segment that changed (old folder names, old barrel paths). Each hit is either a real reference to update or a false positive (string literal, comment, unrelated match) — classify and update only the real ones.

Also update: documentation that references the old structure (README, ARCHITECTURE.md, storybook stories, JSDoc `@module` tags), test fixtures that hardcode paths, and CI config that references the old layout.

Completion criterion: a project-wide content search for every old path segment returns zero real references. Remaining hits are false positives you can justify.

### Step 10 — Run validations

Run every validator the project exposes. Detect them from `package.json` scripts, `pyproject.toml`/`setup.cfg`/`Makefile`, and CI config:

- Type checking: `tsc --noEmit`, `mypy`, `pyright`.
- Lint: `eslint`, `ruff`, `flake8`, `pylint`.
- Build: `npm run build`, `pytest --collect-only` (compile check), `cargo check`, `go build ./...`.
- Tests: `npm test`, `pytest`, `go test ./...`. Run the full suite, not just tests under `TARGET_PATH` — external tests may import from it.
- Path/alias check: `tsc --noEmit` catches broken path aliases; for Python run `python -c "import <module>"` for each top-level package that moved.

If a validator does not exist, note it in the final report under "validations executed" with status `not-available`. Do not silently skip it.

Completion criterion: every available validator has been run and its result recorded (pass/fail). Failures are fixed before declaring done; if a failure is pre-existing and unrelated, record it as a pre-existing risk, not a new failure.

### Step 11 — Review the diff and fix broken references

```
git -C <PROJECT_ROOT> diff --stat
git -C <PROJECT_ROOT> diff
```

Scan the diff for: missed import rewrites, accidental logic changes, files that moved but lost content, files that stayed without a recorded reason. Fix any broken reference you find.

Completion criterion: the diff contains only path/import/barrel/config changes plus the new plan artifact. No line of business logic is in the diff unless it was already in a prior commit.

### Step 12 — `verify` mode

`verify` does not move anything. It re-runs Step 10 validations, then checks:

- `find <TARGET_PATH> -type f` matches the stays-in-place list exactly.
- No empty directory under `TARGET_PATH`.
- No project-wide reference to any old path segment that was supposed to be removed.
- The plan artifact's move map matches the on-disk state (every `destination` exists, every `source` no longer exists unless it is in stays-in-place).
- A `git status` shows only the expected changes (or is clean if the migration was already committed).

Completion criterion: all checks pass; any discrepancy is listed in the final report as a risk, not silently dropped.

## Final Report

Every run (any mode) ends with a report containing these exact sections, in this order:

1. **Analysis summary** — capabilities found, file count, move count, deletion count.
2. **Resulting directory tree** — the on-disk tree under `TARGET_PATH` after the run (use `find <TARGET_PATH> -type d` or `tree` if available).
3. **Moved files** — list of `source → destination`.
4. **Modified files** — list with a one-line reason each (e.g. "import path updated", "barrel re-export added", "tsconfig path alias updated").
5. **Deleted files** — list with evidence for each.
6. **Imports and references updated** — list of files whose imports/exports/aliases changed, grouped by "inside TARGET_PATH" and "outside TARGET_PATH".
7. **Content that stayed in TARGET_PATH and why** — the stays-in-place list with a concrete reason per file.
8. **Validations executed and results** — each validator, command run, pass/fail, and any failure classified as new vs pre-existing.
9. **Risks or pending issues** — ordered by severity. Include any skipped deletion whose evidence was weak, any validator that was unavailable, and any external area that had to be touched to fix references.

If any section is empty, state "None." explicitly — do not omit the section.

## Incremental & Repeatable Execution

The skill is designed to run many times over the same project, once per subpath. To keep runs consistent:

- Every run reads the plan artifact dir `<PROJECT_ROOT>/.hermes/screaming-arch/` to discover prior decisions. Capability names, folder conventions, and the `shared/` policy established by earlier runs are reused, not reinvented.
- Before proposing a new capability folder, check whether a sibling path already established one with the same name — if so, merge into it instead of creating a parallel folder.
- The stays-in-place list from a prior run is authoritative: do not re-move a file a previous run decided to keep, unless the user explicitly overrides.
- After each successful `apply`, append a one-line summary to `<PROJECT_ROOT>/.hermes/screaming-arch/RUNLOG.md` with date, target path, file count, and run mode.