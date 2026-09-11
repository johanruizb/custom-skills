---
name: init-deep
description: |
  Deeply analyze the current repository and generate or update a hierarchy of AGENTS.md files.
  Use when the user asks to initialize agent instructions, create project context files for coding agents,
  says "init-deep", "inicializa contexto", "genera AGENTS.md", or wants coding-agent documentation
  derived from the actual repository. Produces a root AGENTS.md plus directory-level files only where
  local context is clearly useful.
license: MIT
metadata:
  version: "1.0.0"
---

# init-deep

Deep repository-context initialization. Analyze the repository and create a useful hierarchy of `AGENTS.md` files for coding agents.

## Non-negotiable rules

- Generate or update `AGENTS.md` files only.
- Never create or modify `CLAUDE.md`.
- You may read existing `CLAUDE.md` files only as source material for migration or preservation.
- If both `AGENTS.md` and `CLAUDE.md` exist, treat `AGENTS.md` as the canonical target.
- Do not create noisy, generic, redundant, or boilerplate context files.
- Prefer fewer, more useful `AGENTS.md` files over many shallow ones.
- Do not invent commands, architecture, or conventions. Derive them from repository files.

## Purpose

The generated context should help future coding agents quickly understand:

- What the project does.
- How the repository is structured.
- How to install, run, test, lint, typecheck, and build.
- Where important code lives.
- Which conventions matter.
- Which files or patterns should not be touched casually.
- Which commands should be used for verification.
- Which local rules apply in important subdirectories.

Create:

- A root `AGENTS.md` for project-wide guidance.
- Directory-level `AGENTS.md` files only where local context is clearly useful.

## Arguments

Interpret arguments from the user's request.

### `--create-new`

Regenerate the `AGENTS.md` hierarchy cleanly.

### `--max-depth=N`

Limit candidate directories to depth `N`.

Default: `6`

Examples:

- `init-deep`
- `init-deep --create-new`
- `init-deep --max-depth=2`
- `init-deep --create-new --max-depth=4`

If no flags are provided, run in update mode.

Behavior: see Phase 6.

## Working rules

Use available filesystem, search, read, and edit tools.

Before writing any file:

1. Check whether it exists.
2. If it exists, read it.
3. Edit it carefully (prefer targeted edits over full overwrite).
4. If it does not exist, create it.

Never use a destructive overwrite on an existing `AGENTS.md`.

Do not create `AGENTS.md` files in:

- `.git`
- `node_modules`
- `vendor`
- `dist`
- `build`
- `coverage`
- `.next`
- `.nuxt`
- `.turbo`
- `.cache`
- generated output directories
- dependency directories
- binary asset directories

Exception: You may create an `AGENTS.md` in a generated-code source directory only if the file clearly explains "do not edit manually" rules.

## Phase 0 — Track work

Track the phases as working state (todo list if available):

1. Phase 1 — Repository discovery: discover repository structure and existing context files.
2. Phase 2 — Deep analysis: analyze architecture, commands, conventions, and hotspots.
3. Phase 3 — Candidate directory scoring: score candidate directories.
4. Phase 4 — Root `AGENTS.md` structure: generate or update root `AGENTS.md`.
5. Phase 5 — Directory-level `AGENTS.md` structure: generate or update useful directory-level `AGENTS.md` files.
6. Phase 6 — Write behavior: generate or update the selected files in update or create-new mode.
7. Phase 7 — Review and trim: review, deduplicate, trim, and report.

Keep the todo list updated as you work.

## Phase 1 — Repository discovery

Start by identifying the repository root and structure.

Run discovery commands, adapting if needed:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null || true
git branch --show-current 2>/dev/null || true
git rev-parse --short HEAD 2>/dev/null || true
```

Map directory depth:

```bash
find . \
  -type d \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.nuxt/*' \
  -not -path '*/.turbo/*' \
  -not -path '*/.cache/*' \
  | awk -F/ '{print NF-1}' | sort -n | uniq -c
```

List representative files:

```bash
find . \
  -type f \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.nuxt/*' \
  -not -path '*/.turbo/*' \
  -not -path '*/.cache/*' \
  | sed 's|^\./||' \
  | sort \
  | head -300
```

Find important config and context files:

```bash
find . \
  -type f \( \
    -name "README.md" -o \
    -name "AGENTS.md" -o \
    -name "CLAUDE.md" -o \
    -name "package.json" -o \
    -name "pnpm-workspace.yaml" -o \
    -name "yarn.lock" -o \
    -name "package-lock.json" -o \
    -name "bun.lockb" -o \
    -name "turbo.json" -o \
    -name "nx.json" -o \
    -name "pyproject.toml" -o \
    -name "requirements.txt" -o \
    -name "uv.lock" -o \
    -name "poetry.lock" -o \
    -name "go.mod" -o \
    -name "Cargo.toml" -o \
    -name "Makefile" -o \
    -name "Dockerfile" -o \
    -name "docker-compose.yml" -o \
    -name ".editorconfig" -o \
    -name "tsconfig.json" -o \
    -name "vite.config.*" -o \
    -name "next.config.*" \
  \) \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  | sort
```

Also inspect, when present:

- README files.
- Package/workspace manifests.
- Build configs.
- Test configs.
- CI workflows.
- Docker files.
- Entry points.
- App/router/module boundaries.
- Existing `AGENTS.md`.
- Existing `CLAUDE.md` as read-only source material only.

Read them.

Extract useful facts:

- Setup commands.
- Development commands.
- Test commands.
- Build commands.
- Architecture notes.
- Code style rules.
- Naming conventions.
- Testing conventions.
- Security rules.
- Prohibited patterns.
- Directory-specific guidance.
- Generated-code warnings.

Preserve only facts that are:

- Specific to this repository.
- Still supported by files/configs.
- Useful for future coding agents.

Discard:

- Generic advice.
- Stale commands.
- Contradictions.
- Duplicated parent guidance.
- Vague preferences.
- Long prose that does not change agent behavior.

## Phase 2 — Deep analysis

Analyze the repository before writing.

Look for:

- Main language and framework.
- Package manager.
- Monorepo layout.
- Runtime entry points.
- App boundaries.
- Shared libraries.
- Config files.
- Test locations.
- Lint/typecheck/build commands.
- Generated files.
- Database/schema/migration areas.
- API boundaries.
- UI/component conventions.
- Naming conventions.
- Environment variable patterns.
- Security-sensitive code.
- Performance-sensitive code.
- Deprecated modules.
- Risky or complex areas.

When useful, inspect:

- `package.json` scripts.
- `Makefile` targets.
- CI commands.
- Test setup files.
- Docker compose services.
- Framework config.
- Nearby files in important directories.
- Existing docs.

Do not guess commands. Only include commands that are present in the repository or clearly inferable from existing config.

## Phase 3 — Candidate directory scoring

Always create or update: `./AGENTS.md`

Consider directory-level `AGENTS.md` files for directories up to `--max-depth`.

Score a directory as strong if it has several of:

- Its own package/module boundary.
- Its own config.
- Its own tests.
- Many source files.
- Different conventions from parent.
- Important entry points.
- Public API surface.
- Database/schema/migration logic.
- Generated-code rules.
- Security-sensitive code.
- Performance-sensitive code.
- Distinct domain language.
- Complex integration code.
- Frequent future editing likelihood.

Create directory-level files only for strong candidates. Skip weak candidates. Do not create local `AGENTS.md` files that merely repeat the root file.

## Phase 4 — Root AGENTS.md structure

The root `AGENTS.md` should be concise, factual, and useful.

Target length: 80 to 180 lines. Shorter is better if the project is small.

Use this structure:

```md
# AGENTS.md

## Project Overview

Briefly describe what this project is, what it does, and the primary stack.

## Repository Structure

List only meaningful directories.

Example:

- `src/` — application source.
- `tests/` — test suite.
- `packages/*` — workspace packages.

## Where To Look

| Task | Location | Notes |
|---|---|---|
| Find app entry point | `...` | ... |
| Update API routes | `...` | ... |
| Update shared types | `...` | ... |
| Add tests | `...` | ... |

## Commands

# install
...

# development
...

# test
...

# lint
...

# typecheck
...

# build
...

## Architecture Notes

Capture project-specific boundaries, data flow, runtime assumptions, and integrations.

## Coding Conventions

List only conventions actually used in this repository.

## Testing Guidelines

Explain test layout, test commands, fixtures, mocks, and verification expectations.

## Generated Code and External Assets

Explain what should not be edited manually.

## Agent Workflow

- Read the nearest `AGENTS.md` before editing files in a directory.
- Prefer the smallest relevant verification command before broader checks.
- Follow existing neighboring patterns before introducing new ones.
- Do not change public APIs, schemas, or migrations without checking related tests and call sites.
- Keep changes focused and avoid opportunistic refactors.

## Do Not

List repository-specific anti-patterns and risky actions.
```

Adapt headings if the project needs different names, but keep the content practical.

## Phase 5 — Directory-level AGENTS.md structure

For each selected subdirectory, create or update `AGENTS.md`.

Target length: 30 to 90 lines.

Use this structure:

```md
# AGENTS.md

## Scope

Explain what this directory owns.

## Local Structure

List only meaningful local files/directories.

## Local Commands

# test this area
...

## Local Conventions

Only rules that differ from or refine the parent `AGENTS.md`.

## Testing

Local test files, mocks, fixtures, or verification guidance.

## Do Not

Directory-specific anti-patterns or risky actions.
```

Omit sections that have no content (e.g. Local Commands if there are none).

Rules:

- Do not repeat root-level content.
- Do not document every file.
- Do not add generic framework advice.
- Prefer precise, local, actionable instructions.
- Make the file useful when an agent is editing that subtree.

## Phase 6 — Write behavior

### Update mode (default)

- Update existing `AGENTS.md` files.
- Create new `AGENTS.md` files only for strong candidates.
- Preserve useful existing information.
- Remove stale or redundant information.
- Avoid creating too many files.

### Create-new mode (`--create-new`)

- Read all existing `AGENTS.md` files.
- Preserve useful project-specific knowledge.
- Regenerate selected `AGENTS.md` files cleanly.
- Remove stale content from regenerated files.
- Do not delete old files unless the user explicitly asked for deletion.

## Phase 7 — Review and trim

After writing, review all changed `AGENTS.md` files.

Remove:

- Generic advice.
- Duplicate parent content.
- Unsupported guesses.
- Long explanations.
- Obvious statements.
- Stale commands.
- Contradictions.
- Tool-specific content that does not belong in `AGENTS.md`.

Verify:

- Root `AGENTS.md` is useful from the repository root.
- Directory-level files are only present where local context matters.
- Commands match actual project files.
- Generated/vendor directories were not touched.
- No `CLAUDE.md` file was created or modified.
- Existing `CLAUDE.md` content, if read, was used only as migration source material.
- The hierarchy is not excessive.

## Final response

End with this compact report:

```text
=== init-deep Complete ===
Target: AGENTS.md
Mode: update | create-new
Max depth: N

Files created:
- ...

Files updated:
- ...

Files left unchanged:
- ...

Files read as source material:
- ...

Directories analyzed: N

Context hierarchy:
- ./AGENTS.md
- ./path/to/AGENTS.md

Notes:
- ...
```

Keep the final report short.