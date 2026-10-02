---
name: git-commit
description: |
  Commit the current changes autonomously. Use when the user explicitly asks to commit
  or invokes /git-commit. For message-only requests, use a commit-message skill instead.
license: MIT
allowed-tools: Bash(git:*), Read, Write, Edit, Glob, Grep
---

# git-commit

Commit from the current task context. Keep an existing changelog current. Preserve
every change outside the intended commit.

## State

`.commit/` at the repo root is the commit memory: the conventions learned about this
repository, so later runs keep them instead of rediscovering them. One split, two
files: `config.json` holds what a script could read; `conventions.md` holds what
only prose can — the reasons behind values, the gotchas, the human's standing
preferences. `.commit/` is ordinary tracked content: it joins the commit that taught
it, so clones carry the same conventions.

Read `.commit/` when it exists. When it is absent or stale, learn from the repo
during that run: scan the root for `CHANGELOG*`, `CHANGES*`, `HISTORY*` and pick the
file with recent entries; no match is a finding too — no changelog exists, nothing
will be extended, and this skill never creates one. Write what was learned before
anything is committed, and never re-ask what `.commit/` answers. It stores
conventions, never permission: every Safety stop is confirmed fresh on every run.

### config.json

The conventions in machine form. Omit fields the repo does not use:

```json
{
  "conventions": {
    "changelog": "CHANGELOG.md"
  }
}
```

- `changelog` is the file each commit extends. Omit it when the repo has no
  changelog, and when release tooling generates the file (git-cliff,
  release-please) — the tool owns the entries.
- Stale when the configured file no longer exists, or when nothing is configured
  and a changelog has appeared. Fall back to re-learning and rewrite.

### conventions.md

Natural language, not config. Three things belong there, one short section per
theme:

- **Why**: the reason behind each non-default value ("entries under `Unreleased`
  because release tooling cuts the released sections from it").
- **Gotchas**: what a next run would rediscover the hard way ("PRs squash-merge, so
  changelog entries reference the PR number"; "the changelog is in Spanish").
- **Preferences**: what the human corrected once, applying from the next commit on
  ("docs commits earn no entries").

When a run contradicts a line here, rewrite it; prose goes stale like paths do.

## Fast path

1. Reuse the task intent and paths already known. Reuse the diff you just created.
2. If Git state is unknown, run `git status --short --branch` and `git diff --cached --stat`.
3. Read `.commit/` (§ State): a fresh state governs this run; an absent or stale one
   is learned from the repo and written before anything is committed.
4. Write the changelog entry (§ Changelog) and refresh `.commit/` with anything this
   run learned — both ride inside the commit, never after it.
5. If the index has changes, stage what step 4 wrote on top of it — nothing else —
   then commit exactly the result without confirmation unless a Safety stop
   condition applies:
   `git commit --message "type(scope): summary"`.
6. If the index is empty, stage only known task paths together with what step 4
   wrote, then commit:
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

## Changelog

When `config.json` names a changelog, a commit changing user-facing behavior extends
it before `git commit` runs — Safety stops settled first, so an entry is never
written for a commit that will not happen. Nothing configured, nothing written.

Keep a Changelog 1.1.0 (https://keepachangelog.com/en/1.1.0/) is the changelog
format of record: whatever the file in place leaves open — a missing `## [Unreleased]`
above all — comes from the standard.

- An entry for every user-facing commit: `feat`, `fix`, `perf`, reverts, security,
  removals. Chores, tests, build, CI, and internal refactors earn none — finer rules
  the repo settled live in `.commit/conventions.md`.
- Read the top of the file before writing: follow the format in place — heading
  levels, bullet style, entry language, link style — and place the entry where the
  file collects not-yet-released changes. Under the standard's categories, with
  `###` headings inside `## [Unreleased]`, map `feat` → Added, `fix` → Fixed,
  `perf` → Changed, removals and `revert` → Removed, security → Security.
- One concise bullet, phrased for the user of the project, not the committer: what
  changed in behavior, not which commit did it.
- Append-only: a new bullet for this commit; existing lines and released sections
  stay untouched. `Unreleased` is release tooling's raw material.
- Uncommitted human edits in the file: ask before staging — unclaimed work
  (§ Pre-commit checklist).

Done when the entry stands under the right category, in the file's own format, and
is staged with the commit it describes.

## Inspect only when needed

For pre-existing, mixed, or unexpectedly large changes, read only the target diffs needed
to determine intent. Read `references/conventional-commits.md` only when the type or
breaking-change format is unclear.

## If a hook fails

Report the hook's output. Retry a normal commit only after an in-scope fix, revalidation,
and confirmation that the failed attempt did not create a commit (`git rev-parse HEAD`
before and after).

## Pre-commit checklist

Every commit satisfies each check before running:

- **Scoped staging.** Never `git add .`/`git add -A` unscoped; stay in the current
  repository and never `cd` or ask for a path.
- **No mixed set.** With a non-empty index, the only `git add` allowed is what this
  run authored for the commit itself — the changelog entry and `.commit/` — never a
  task path; never path arguments to `git commit`, they silently drop other staged
  changes.
- **Hooks run.** Plain `git commit --message` form, no additional flags; never
  `--no-verify` (`-n`). For a failing hook, use *If a hook fails*.
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