---
name: git-commit
description: |
  Execute git commit with conventional commit message analysis, intelligent staging, and message generation.
  Supports:
  (1) Auto-detecting type and scope from changes
  (2) Generating conventional commit messages from diff
  (3) Interactive commit with optional type/scope/description overrides
  (4) Intelligent file staging for logical grouping
license: MIT
allowed-tools:
  - Bash
---

# git-commit

Create standardized, semantic git commits using the Conventional Commits specification by analyzing the actual code diff to determine the appropriate type, scope, and message content.

## Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

### Breaking Changes

Two supported formats:

1. Exclamation mark after type/scope: `feat!: remove deprecated endpoint`
2. BREAKING CHANGE footer:

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

## Workflow

### 1. Analyze Diff

- If files are staged: `git diff --staged` to see staged changes
- If nothing staged: `git diff` plus `git status --porcelain` to see working tree changes

### 2. Stage Files (if needed)

When nothing is staged or you want different grouping:

- Stage specific files: `git add path/to/file1 path/to/file2`
- Stage by pattern: `git add *.test.*` or `git add src/components/*`
- Interactive staging: `git add -p`

> **Never commit secrets:** Watch for `.env`, `credentials.json`, private keys, or other sensitive files.

### 3. Generate Commit Message

Analyze the diff to determine:

- **Type** — What kind of change (from the types table above)
- **Scope** — What area/module is affected (optional but recommended)
- **Description** — One-line summary in present tense, imperative mood, under 72 characters

### 4. Execute Commit

Single-line form:

```bash
git commit -m "<type>[scope]: <description>"
```

Multi-line with body/footer:

```bash
git commit -m "$(cat <<'EOF'
<type>[scope]: <description>

<optional body>

<optional footer>
EOF
)"
```

## Best Practices

- One logical change per commit
- Present tense imperative mood: "add" not "added" or "adds"
- Reference issues: "Closes #123", "Refs #456"
- Keep description under 72 characters

## Git Safety Protocol

1. NEVER update git config
2. NEVER run destructive commands (`--force`, `hard reset`) without explicit user request
3. NEVER skip hooks (`--no-verify`) unless the user asks
4. NEVER force push to main/master
5. If a commit fails due to hooks, fix the issue and create a NEW commit — do not amend

---

*Forked from [github/awesome-copilot](https://github.com/github/awesome-copilot). MIT licensed.*
