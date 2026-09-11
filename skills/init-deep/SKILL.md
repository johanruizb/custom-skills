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

- Write only `AGENTS.md` files: the root file plus subtree files for strong candidates.
- Never create or modify `CLAUDE.md`.
- Treat existing `CLAUDE.md` files as read-only source material for migration or preservation.
- If both `AGENTS.md` and `CLAUDE.md` exist, treat `AGENTS.md` as the canonical target.
- Write context files that are specific, non-redundant, and free of boilerplate.
- Prefer fewer, more useful `AGENTS.md` files over many shallow ones.
- Derive every command, architecture note, and convention from repository files.

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

Run these from the repository root:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null || true
git branch --show-current 2>/dev/null || true
git rev-parse --short HEAD 2>/dev/null || true
```

Map directory depth, list representative files, and find important config and context files with the discovery pipelines in `references/discovery.md`.

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

Strong = 3 or more signals below, or a self-contained package boundary with its own config or tests.

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

Done when every candidate within `--max-depth` is scored and the selected set is listed in the todo.

## Phase 4 — Root AGENTS.md structure

The root `AGENTS.md` should be concise, factual, and useful.

Target length: 80 to 180 lines. Shorter is better if the project is small.

Use the template in `references/templates.md` (example skeleton; prune anything not repo-specific and omit empty sections).

Adapt headings if the project needs different names, but keep the content practical.

## Phase 5 — Directory-level AGENTS.md structure

For each selected subdirectory, create or update `AGENTS.md`.

Target length: 30 to 90 lines.

Use the directory template in `references/templates.md`.

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