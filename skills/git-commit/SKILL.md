---
name: git-commit
description: |
  Execute a local Git commit quickly and autonomously in the current repository.
  Use when the user explicitly asks to commit changes, run git commit, or invokes /git-commit.
  For message-only requests, use a commit-message skill instead.
license: MIT
allowed-tools:
  - Bash(git:*)
  - Bash(bash:*)
---

# git-commit

Commit from the current task context. Preserve every change outside the intended commit.

## Fast path

1. Reuse the task intent and paths already known. Do not reread a diff you just created.
2. Resolve `scripts/prepare_commit.sh` relative to this `SKILL.md`; keep the repository `cwd`.
3. If Git state is unknown, run `bash <helper> inspect`.
4. If the index has changes, commit exactly that staged set:
   `bash <helper> commit --message "type(scope): summary"`.
5. If the index is empty, stage only known task paths:
   `bash <helper> commit --message "type(scope): summary" -- path...`.

Do not ask for normal confirmation, type, scope, message, or file selection.
The helper validates the message, selected filenames, repository state, and
`git diff --cached --check` before committing.

## Scope and message

- Treat an existing staged set as authoritative. Never add unstaged files to it.
- Default to one cohesive commit. Keep implementation, tests, docs, config, and lockfiles
  together when they serve one intent.
- Split only changes with independent intent that can be reverted independently. Never split
  by file kind or Conventional Commit type alone.
- Use `type(scope): imperative summary`; scope is optional and the subject must be at most
  72 characters. Match the repository language and established scope names.
- Add a body only for non-obvious rationale, breaking changes, migrations, security,
  reverts, or issue references.

## Inspect only when needed

For pre-existing, mixed, unknown, or unexpectedly large changes, run `bash <helper> inspect`,
then read only targeted diffs needed to determine intent. Read
`references/conventional-commits.md` only when the type or breaking-change format is unclear.

## Safety

- Stay in the current repository. Never `cd`, ask for a path, or run an unscoped
  `git add .`/`git add -A`.
- Stop for explicit confirmation only when a sensitive path is selected for the commit,
  the repository is on a detached `HEAD`, or ownership of uncommitted work cannot be
  determined safely. After confirmation, pass the corresponding explicit override;
  never infer that permission.
- Never update Git config, amend, reset, push, force, bypass hooks, or discard unrelated
  work as part of this skill. Never add co-author or AI attribution.
- If a hook fails, report its output. Retry a normal commit only after an in-scope fix,
  revalidation, and confirmation that the failed attempt did not create a commit.
