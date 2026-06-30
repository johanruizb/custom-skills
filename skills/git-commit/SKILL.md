---
name: git-commit
description: |
  Execute git commit autonomously with conventional commit message analysis, atomic logical grouping, and message generation.
  Operates on the current working directory (cwd) without asking the user for paths or confirmation.
  Supports:
  (1) Auto-detecting type and scope from changes
  (2) Generating conventional commit messages from diff
  (3) Autonomous commit without user confirmation (Safety Protocol exceptions still require explicit request)
  (4) Splitting changes into multiple atomic commits grouped by logical type/scope
license: MIT
allowed-tools:
  - Bash
---

# git-commit

Create standardized, semantic git commits using the Conventional Commits specification by analyzing the actual code diff to determine the appropriate type, scope, and message content.

## Autonomy, Atomicity, and Path

These three rules govern every execution and override the legacy "interactive" behavior:

1. **No questions — proceed autonomously.** Never ask the user to confirm a normal commit, choose a type/scope, approve a message, or select files. Detect everything from the diff and commit directly. The only permitted questions are the explicit Safety Protocol exceptions listed in the *Git Safety Protocol* section (`--force`, hard reset, `--no-verify`), which always require an explicit user request.
2. **Prefer more, atomic commits.** Split changes into multiple commits — one per logical type/scope (e.g., `feat`, `fix`, `docs`, `refactor`) — instead of a single commit. Group files that belong to the same logical change together; do not split one logical change across commits. If the entire change is a single logical type, one commit is correct — never force an artificial split.
3. **Operate on the current path (cwd).** Run every `git` command in the current working directory. Never `cd` into another path, never ask the user for a path, and never assume a repo root elsewhere. Subdirectories of the repo are staged normally (`git add <path>` relative to cwd).

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

### 1. Analyze Diff (in cwd)

- If files are staged: `git diff --staged` to see staged changes
- If nothing staged: `git diff` plus `git status --porcelain` to see working tree changes
- Run all commands in the current working directory — no `cd`, no asking the user for a path

### 2. Group Changes into Logical Commits

Before staging, partition the changed files into one group per logical type/scope (e.g., `feat`, `fix`, `docs`, `refactor`). Each group becomes one atomic commit. If all changes share a single logical type, there is one group — do not split artificially.

### 3. Stage Files (if needed)

For each logical group, stage exactly the files that belong to it:

- Stage specific files: `git add path/to/file1 path/to/file2` (paths relative to cwd)
- Stage by pattern: `git add *.test.*` or `git add src/components/*`

> **Never commit secrets:** Watch for `.env`, `credentials.json`, private keys, or other sensitive files.

### 4. Analyze Previous Commit Style

Before generating the message, inspect recent commit history to match the project's conventions:

```bash
git log --oneline -20
```

Determine from recent commits:

- **Language** — Match the language used in previous commits (English, Spanish, etc.). If the repo uses Spanish descriptions, write in Spanish. If English, use English. Always follow the existing convention.
- **Tone and style** — Formal vs informal, abbreviated vs full words, use of emojis, capitalization patterns, etc.
- **Scope naming** — Follow the same scope naming pattern used in history (e.g., `api`, `auth`, `ui`, `core`).
- **Description conventions** — Imperative mood, past tense, or whichever pattern is already established in the repo.
- **Body usage** — Whether commits typically include a body or are single-line only.

> **Consistency is critical.** The new commit must blend in naturally with the existing history. When in doubt, follow the majority pattern.

### 5. Generate Commit Message

Analyze the diff to determine:

- **Type** — What kind of change (from the types table above)
- **Scope** — What area/module is affected (optional but recommended)
- **Description** — One-line summary matching the language and style of previous commits, under 72 characters

### 6. Execute Commit (autonomously, once per logical group)

Proceed without asking the user for confirmation. Run one commit per logical group staged in step 3.

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

- **Prefer multiple atomic commits over one large commit** — one commit per logical type/scope (see *Autonomy, Atomicity, and Path* above). Do not bundle unrelated types into a single commit.
- One logical change per commit
- Present tense imperative mood: "add" not "added" or "adds" (unless repo history uses a different convention)
- Reference issues: "Closes #123", "Refs #456"
- Keep description under 72 characters
- **No co-authorship trailers** — Never add `Co-authored-by:`, `Generated with`, or any attribution footer referencing Claude, Copilot, AI assistants, or any other tool. Commits must look authored entirely by the human contributor.
- **Match existing commit style** — Language, tone, formatting, and conventions must be consistent with the repository's commit history (see step 3 above)

## Git Safety Protocol

These rules are the **only exceptions** to the autonomous no-questions rule. They always require an explicit user request before execution; never run them autonomously.

1. NEVER update git config
2. NEVER run destructive commands (`--force`, `hard reset`) without explicit user request
3. NEVER skip hooks (`--no-verify`) unless the user asks
4. NEVER force push to main/master
5. If a commit fails due to hooks, fix the issue and create a NEW commit — do not amend

---

*Forked from [github/awesome-copilot](https://github.com/github/awesome-copilot). MIT licensed.*
