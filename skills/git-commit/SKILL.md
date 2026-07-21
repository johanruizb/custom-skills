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

Create standardized, semantic git commits using Conventional Commits. A script handles the mechanical data collection; the LLM handles the semantic decisions.

## Workflow

### 1. Collect data (script)

```bash
bash scripts/prepare_commit.sh
```

Optional flags: `--staged` (staged only), `--unstaged` (unstaged only).

The script outputs: status, diff, recent commit history (style reference), secret detection, and heuristic type hints per file.

### 2. Group changes into atomic commits

Partition changed files into one group per logical type/scope. Each group becomes one commit. If all changes share a single logical type, one commit is correct — do not split artificially.

### 3. Determine type and scope

Use the type hints from the script as a starting point, then read the actual diff to confirm. See `references/conventional-commits.md` for the full type table and format.

### 4. Match existing commit style

Read the recent commits from the script output. Match:
- **Language** — Spanish, English, etc. (follow the majority)
- **Tone** — formal/informal, abbreviated/full, emojis, capitalization
- **Scope naming** — `api`, `auth`, `ui`, etc.
- **Body usage** — single-line vs multi-line

### 5. Generate message and commit (autonomously)

No questions. Commit directly once per logical group.

```bash
git add <files for this group>
git commit -m "<type>[scope]: <description>"
```

Multi-line:
```bash
git commit -m "$(cat <<'EOF'
<type>[scope]: <description>

<optional body>
EOF
)"
```

## Rules

- **Autonomous:** Never ask the user to confirm a normal commit, choose a type/scope, approve a message, or select files. Detect everything from the diff.
- **Atomic:** Prefer more, atomic commits — one per logical type/scope. Do not bundle unrelated types.
- **cwd only:** Run all git commands in the current working directory. Never `cd`, never ask for a path.
- **No secrets:** If the script flags sensitive files, do NOT commit them without explicit user confirmation.
- **No co-authorship trailers:** Never add `Co-authored-by:`, `Generated with`, or any AI attribution.
- **Description < 72 characters.** Imperative mood unless repo history uses a different convention.
- **Consistency:** The commit must blend with existing history.

## Safety Protocol

These are the ONLY exceptions to autonomous execution. Always require explicit user request:

1. NEVER update git config
2. NEVER run `--force` or hard reset without explicit request
3. NEVER use `--no-verify` unless the user asks
4. NEVER force push to main/master
5. If a commit fails due to hooks, fix the issue and create a NEW commit — do not amend

## Reference Files

- `references/conventional-commits.md` — Type table, format, breaking changes, decision guide
- `scripts/prepare_commit.sh` — Data collection script (status, diff, log, secret scan, type hints)