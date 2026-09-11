# Output templates

Example skeletons only. Prune anything not repo-specific and omit empty sections.

## Root `AGENTS.md`

````md
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

## Do Not

List repository-specific anti-patterns and risky actions. Omit this section if there is nothing repo-specific to list.
````

## Directory-level `AGENTS.md`

````md
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
````
