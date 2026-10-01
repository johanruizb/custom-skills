---
name: fork-pr
description: "Sync a fork's branch upstream: push it to origin, then open a PR in the original repo and keep its title, body, and CI badges refreshed on every run. Use when the repo is a fork and the user asks to sync a branch upstream, open a PR from the fork, or refresh an existing fork PR. Triggers: 'sync my fork to upstream', 'fork PR', 'sincronizar el fork con upstream', 'abrir PR desde el fork', 'actualizar el PR de mi fork'."
license: MIT
allowed-tools: Bash(git:*), Bash(gh:*), Read, Write, Glob, Grep
metadata:
  author: johanruizb, Hermes Agent
  version: "1.0.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [git, github, pull-request, fork, upstream, sync, ci-badges]
    related_skills: [git-commit]
---

# fork-pr

## Overview

The repo is a fork; branch `X` holds the fork's work; the repo it came from is the
**parent**. One run leaves one PR in the parent — base its `BASE` branch, head
`fork:X` — that is a faithful copy of the fork's state: pushed, open, titled,
bodied, badged.

Two properties make repeated runs cheap:

- **Idempotent refresh** — the PR text is regenerated from the current branch state
  every run: same branch, same title, same body. The run opens the PR or refreshes
  the existing one; it never stacks a second.
- **Single source of PR text** — the title comes from the commit range, the body
  from the template in §Phase 4, the badges from `.github/workflows/`. No other
  place maintains the text, so a run that changes the branch text has only one edit.

## When to Use

- "sync branch X upstream", "publish my fork's branch", "open a PR from this fork",
  "refresh the fork PR"
- 'sincronizar mi fork con upstream', 'abrir PR desde el fork',
  'actualizar el PR de mi fork'

Don't use when the repo is not a fork (there is no parent to verify) or when the
goal is updating the fork **from** upstream — that direction is GitHub's Sync fork,
not a PR upstream.

## Phase 1: Verify the fork and resolve the branches

```bash
gh repo view --json isFork,nameWithOwner,parent
```

`isFork` must be true and `parent.nameWithOwner` names the parent. When `isFork` is
false, stop and report that fact — nothing downstream has a parent to work with.

Resolve the two branches:

- `X` — the branch argument, or `git branch --show-current`.
- `BASE` — the same-named branch in the parent when it exists
  (`git ls-remote --heads <parent-url> X`), else the parent's default branch
  (`gh repo view <parent> --json defaultBranchRef`). When `X` exists in the parent
  and the intended base reads differently, ask — the base is a published decision,
  not a guess.

Fetch the parent: `git remote get-url upstream || git remote add upstream
$(gh repo view <parent> --json url --jq .url)`, then `git fetch upstream`.

**Done when:** fork confirmed, `X` and `BASE` resolved, `upstream/BASE` fetched.

## Phase 2: Sync X to origin

Pre-flight: `git status --porcelain` clean. A dirty tree is git-commit's input,
not this skill's — it pushes commits only.

```bash
git fetch origin
git rev-list --left-right --count origin/X...X
```

- First count > 0, second = 0 — the remote is ahead only: nothing to push.
- Second count > 0 — `git push [-u] origin X` (`-u` when origin has no `X` yet).
- Both counts > 0 — diverged history rewrites the open PR: confirm with the human,
  then `git push --force-with-lease origin X`. Never plain `--force`.

**Done when:** `origin/X` equals `X` — both counts 0.

## Phase 3: Locate the PR

```bash
gh pr list -R <parent> --state open --head X \
  --json number,title,url,headRepositoryOwner \
  --jq '.[] | select(.headRepositoryOwner.login == "<fork-owner>")'
```

`--head` takes a bare branch name only — the `owner:branch` syntax is unsupported
on this command — so the JSON filter does the owner matching. One result → that PR
is the target. Several → the oldest is the target; name the rest for the human to
close. None → the create path: draft the text first (§Phase 4), then create with it.

When the existing PR's base differs from the resolved `BASE`, ask before
re-targeting it: `gh pr edit <number> -R <parent> --base <BASE>`.

**Done when:** the target PR number is known, or the create path is chosen.

## Phase 4: Draft the PR text

Collect, in the fork's checkout:

- Commits: `git log --oneline upstream/BASE..X` — only as fresh as the last fetch,
  and Phase 1 fetches every run.
- Workflows: `.github/workflows/*.yml` and `.yaml` — one badge per file.

Title — Conventional Commits, from the commit list:

- One commit → its own subject.
- Several commits → the highest-impact type among them (breaking/`!` first, then
  `feat`, `fix`, the rest), with a summary naming the common thread; when the
  commits are not Conventional Commits, read their diffs and classify by impact.
- Scope: the one the commits share, else the branch name.

Body — regenerated whole every run, never appended to:

```markdown
## What

<one paragraph for the reviewer: what branch X changes in the parent>

## Changes

- <commit subject> (<short hash>)

## Badges

<one badge per workflow, on branch X>

**Commits:** https://github.com/<parent>/compare/<BASE>...<fork-owner>:<X>
```

Badge recipe, one per workflow file `<name>.yml`, label from the file's `name:` key
(fall back to the file name):

```markdown
![<workflow name>](https://github.com/<fork-owner>/<repo>/actions/workflows/<name>.yml/badge.svg?branch=<X>)
```

The badge shows the fork's CI on `X` — the state upstream would merge.

Write the body to `/tmp/opencode/fork-pr-body.md`.

**Done when:** the file matches the template with no `<placeholder>` left, and the
title reads as Conventional Commits.

## Phase 5: Apply and verify

- Create path: show the human the drafted title and body first — creating publishes
  something new — then:

```bash
gh pr create -R <parent> --base <BASE> --head <fork-owner>:<X> \
  --title "<title>" --body-file /tmp/opencode/fork-pr-body.md
```

- Refresh path: apply without an approval loop — the edit is reversible and the PR
  already exists:

```bash
gh pr edit <number> -R <parent> --title "<title>" \
  --body-file /tmp/opencode/fork-pr-body.md
```

Then verify the shipped state:

```bash
gh pr view <number> -R <parent> --json title,body,mergeable,mergeStateStatus,state
```

- Title matches the draft; body carries What, Changes, and Badges.
- `mergeStateStatus` `CONFLICTING` or `DIRTY` → name the conflicts read-only with
  `git merge-tree --write-tree upstream/BASE X` (fall back to
  `git merge --no-commit upstream/BASE` + `git merge --abort`), and hand the human
  the files and the fix path: merging `upstream/BASE` into `X` locally and pushing.
  The PR stays open; the fix is the human's merge, not this skill's push.

**Done when:** the PR is open with template-matched text, mergeable — or the
conflicts are named to the human.

## Common Pitfalls

- **`--head` and org-owned forks** — the `user:branch` syntax rejects an
  organization as the user; an org-owned fork needs the parent's web compare view
  for creating, after which Phase 5 refreshes it normally.
- **Stacked PRs** — the create path runs once per fork branch; every later run goes
  through Phase 3's reuse. A second open PR with the same head is noise to close,
  not a template to copy.
- **Badges without a run** — a workflow that never ran on `X` in the fork shows
  `no status` until the first push triggers it; the badge is honest about the
  fork's CI, which is the state upstream would merge.
- **Force pushes** — a rewritten `X` rewrites the open PR's history out from under
  reviewers; confirm first, and `--force-with-lease` always.

## Verification/Completion Checklist

- `isFork` confirmed; parent, `X`, and `BASE` named.
- Working tree clean; `origin/X` equals `X`.
- Exactly one target PR with head `fork-owner:X` — reused, or created after the
  human saw the draft.
- Title is Conventional Commits; body regenerated from the template (What,
  Changes, Badges, no placeholders left); one badge per workflow, on branch `X`.
- `mergeable` true — or the conflicting files are named to the human with the fix
  path.