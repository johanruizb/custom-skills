---
name: git-commit
description: |
  Commit the current changes autonomously. Use when the user explicitly asks to commit
  or invokes /git-commit. For message-only requests, use a commit-message skill instead.
license: MIT
allowed-tools: Bash(git:*)
---

# git-commit

Commit from the current task context. Preserve every change outside the intended commit.

## Fast path

1. Reuse the task intent and paths already known. Reuse the diff you just created.
2. If Git state is unknown, run `git status --short --branch` and `git diff --cached --stat`.
3. If the index has changes, commit exactly that staged set without confirmation unless a
   Safety stop condition applies:
   `git commit --message "type(scope): summary"`.
4. If the index is empty, stage only known task paths, then commit:
   `git add -- path...` and `git commit --message "type(scope): summary"`.

Choose type, scope, message, and file selection yourself. The Pre-commit checklist below
defines the checks to satisfy before each commit leaves the agent.

## Scope and message

- Treat an existing staged set as authoritative.
- Default to one cohesive commit. Keep implementation, tests, docs, config, and lockfiles
  together when they serve one intent.
- Split only changes with independent intent that can be reverted independently. Never split
  by file kind or Conventional Commit type alone.
- Use `type(scope): imperative summary`; scope is optional and the subject must be at most
  72 characters. Match the repository language and established scope names.
- Unclear type or breaking-change format: read `references/conventional-commits.md`.
- Add a body only for non-obvious rationale, breaking changes, migrations, security,
  reverts, or issue references.

## Inspect only when needed

For pre-existing, mixed, or unexpectedly large changes, read only the target diffs needed
to determine intent. Read `references/conventional-commits.md` only when the type or
breaking-change format is unclear.

## If a hook fails

Report the hook's output. Retry a normal commit only after an in-scope fix, revalidation,
and confirmation that the failed attempt did not create a commit (`git rev-parse HEAD`
before and after).

## Pre-commit checklist

Every commit satisfies all four before running:

- **Scoped staging.** Never `git add .`/`git add -A` unscoped; stay in the current
  repository and never `cd` or ask for a path.
- **No mixed set.** With a non-empty index, commit it as given, never combined with
  `git add`; path arguments to `git commit` silently drop other staged changes.
- **Unclaimed work.** If a selected path is outside the current task and ownership of the
  change is unclear, stop and ask before staging it.
- **Clean subject.** One new commit, no amend/reset/push/force/config; never add co-author
  or AI attribution. A commit subject that already exceeds 72 characters has failed this
  line — rewrite it, do not commit it.

## Safety stops

Confirm with the user and name the reason before committing when any holds:

- A sensitive path enters the commit: `.env*`, `*.pem`, `*.key`, credentials or
  service-account JSON, private keys, or files matching an ignore-style secret pattern the
  repo already uses.
- The repository is on a detached `HEAD`.
- The pre-commit checklist cannot be satisfied safely (unresolvable ownership, conflicting
  index state, active merge/rebase).

After an explicit confirmation, proceed with the corresponding commit. Never infer
permission beyond the confirmed stop.
