---
name: release-to-github
description: "Cut a standardized release: bump the version, write the changelog, commit, tag, and branch. Use when the user asks to release, publish, or tag a new version."
license: MIT
allowed-tools: Bash(git:*), Bash(gh:*), Bash(npm version:*), Read, Write, Edit, Glob, Grep
---

# release-to-github

One skill, many repos: every convention comes from the repository, never from this
skill. Questions come before writes, not after: a standing decision is asked once, on
the first run, and stored in `.release/` so no run asks it again; a per-release one
(the version number, the release notes) is approved before anything is written or
committed. The human cannot undo a push, a GitHub release, or a package publish, so
those run last, after they have seen the release notes.

Before the Survey, write the TODO list the harness understands (its todo tool): one
item per phase plus one per approval (the version, the Go gate in §Ship). Mark an
item completed the moment its phase is done; the list is the running state of the
release.

## State

`.release/` at the repo root is the release memory, committed with every release so
clones and later runs keep the same conventions. One split, two files: `config.json`
holds what a script could read; `conventions.md` holds what only prose can — the
reasons behind the values, the gotchas, the human's standing preferences.

### config.json

The conventions in machine form. Omit fields the repo does not use — no
`githubReleases` or `publishTarget` without them, no `releaseTool` when the bump is
manual:

```json
{
  "conventions": {
    "versionFile": "package.json",
    "changelog": "CHANGELOG.md",
    "changelogLinks": "inline",
    "commitStyle": "conventional",
    "tagPrefix": "v",
    "branchPrefix": "release/",
    "githubReleases": true,
    "publishTarget": "npm",
    "releaseTool": { "name": "npm version", "commits": true, "tags": true }
  },
  "lastRelease": {
    "version": "1.5.0",
    "tag": "v1.5.0",
    "branch": "release/v1.5.0",
    "date": "2026-08-31"
  }
}
```

- `changelogLinks` is `inline` when URLs sit in the entries, `reference-block` when
  the file collects links at the bottom.
- Stale when a cached path (version file, changelog) no longer exists or
  `lastRelease.tag` is not the latest `git tag`. Stale `config.json` falls back to
  the full Survey and is rewritten.

### conventions.md

Natural language, not config. Seeded during the first Survey — as each convention is
discovered, note anything that would surprise a next run — and extended whenever a
release learns something. A question the human answered once becomes a
**Preference** here. Three things belong there, one short section per theme:

- **Why**: the reason behind each non-default value ("branchPrefix is `release/`
  because backport branches fan out from it").
- **Gotchas**: what a next run would rediscover the hard way ("the publish workflow
  waits for the GitHub release to exist first", "tests must pass before tagging").
- **Preferences**: answers given once, for every run after ("never publish in the
  evening"; "push directly, no Go gate"; "chore commits count as release entries").

When the Survey contradicts a line here, rewrite the line; prose goes stale like
paths do.

## Survey

Read the conventions before writing anything. Check `.release/config.json` first:
when present and fresh, its `conventions` are the survey, so run only the pre-flight
checks — and read `conventions.md` too, it carries the judgment the schema cannot.
When absent or stale, discover each convention from the repo:

- Version file: `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `VERSION`.
  Fall back to `git tag --sort=-v:refname | head -n1`.
- Changelog: `CHANGELOG.md` at the root. Offer to create it when missing.
- Commit style: `git log` since the last tag. Fall back to Conventional Commits.
- Tag style: `git tag`. Default `v`-prefixed SemVer (`v1.4.2`).
- Release branch: existing `release/*` branches (`git branch -r`). Each release gets
  a branch named `<branchPrefix><tag>` (`release/v1.5.0`) at the release commit.
- Publish target: release workflow in `.github/workflows`, `publishConfig`, package
  registry config. Local-only when none is found.
- Release tooling: an existing `npm version` / `cargo release` / script. When present,
  run it and skip the manual bump. Note whether it also commits and tags; if it does,
  Ship skips those steps too.

When a convention does not trace to a file or `git` output, ask the human once and
store the answer: machine values in `config.json`, judgment in `conventions.md`
Preferences. Never re-ask what `.release/` answers — that is the point of the
artifact; a cached answer only returns to a question when `git` contradicts it.

Pre-flight checks, before any write:

- Working tree clean (`git status --porcelain`).
- No prior tag with the next version; no existing `<branchPrefix><version>` branch.
- `gh auth status` passes when the repo will get a GitHub release
  (`githubReleases` in `config.json`, or the first run's stored answer).
- No previous tag at all: a first release. The commit range starts at the root commit,
  the changelog omits the full-changelog line, and Version classifies every commit.

Done when every convention traces to `.release/` (config or conventions.md), to a
file, or to `git` output; you can name the bump mechanism you will use (tool, or
manual edit); and every pre-flight check passes or has a decision from the human.

## Version

List the commits since the last tag (`git describe --tags --abbrev=0`; on a first
release, the root commit), then derive the bump from those commits:

- `fix` → patch; `feat` → minor; `!` or a `BREAKING CHANGE` footer → major.
- On `0.x`: breaking bumps minor, `feat` bumps patch.
- Non-conventional commits: read their diffs and classify by user impact.

Propose the next version with the reason (`feat` present → minor). Done when the
human has approved the number and every commit in the range is accounted for — you
can say what each does for the release, and any stray merge or foreign-branch commit
was named to the human before the proposal.

## Changelog

One new section under the released version and today's date. Write new entries; never
rewrite old sections:

```markdown
## [1.5.0] - 2026-08-31 (abc1234)

### Added
### Changed
### Fixed
### Removed
### Deprecated
### Security
```

- Map commit types to headings: `feat` → Added, `fix` → Fixed, `perf`/`refactor` →
  Changed, removal/`revert` → Removed; skip internal chores.
- Drop headings with no entries.
- Append the short hash of the last commit in the release range to the header, so
  each section shows at a glance where it ends; the previous section's hash (or the
  tag) marks where it begins.
- Write entries in plain, specific language (no AI-slop phrasing); when the unslop
  skill is available, run the section through it.
- Phrase each entry for the user of the project, not the committer: what changed in
  behavior, not which commit did it.
- End the section with a full-changelog line, unless this is the first release:
  `**Full changelog:** https://github.com/<owner>/<repo>/compare/vA...vB`. Build it
  from the previous tag, the new one, and `git remote get-url origin`. When the file
  keeps its links in a reference block at the bottom, put the URL there instead of
  inline.

Show the section to the human when it is drafted, not when the release is already
tagged. Done when they have approved it and you can walk the commit list from Version
and point every commit to its entry or its named omission — every user-facing change
has an entry, and every skipped commit was decided, not missed.

## Ship

An interrupted run leaves its work in git: the changelog section, the release commit,
the tag, or the release branch may already exist. Check for them in order and resume
at the first missing one; trust `git` and `gh` over `.release/`, always:

- Changelog section for `<version>` already written.
- Release commit — a commit bumping the version file to `<version>`.
- `git tag -l <tagPrefix><version>`.
- `git branch --list <branchPrefix><version>`.

Refresh `.release/` before step 1: `config.json` gets the Survey's conventions plus
the new `lastRelease`, and `conventions.md` gets anything this run learned. When the
release tooling already committed and tagged (§Survey), skip steps 1-2 but commit the
changelog and the `.release/` refresh when they are still uncommitted:
`chore(release): v<version>`.

1. Commit the version file(s), the changelog, and `.release/` together:
   `chore(release): v<version>`.
2. Tag: annotated, first changelog entry as the subject, the whole new section as the
   body (`git tag -a <tagPrefix><version> -m "<subject>" -m "<body>"`).
3. Branch: `<branchPrefix><tag>` pointing at the release commit, so every version
   keeps a branch to backport fixes onto. Reuse the prefix only when one already
   exists in the repo; default to `release/`.

Then one Go gate, before the irreversible block. Nothing irreversible runs before
this approval:

4. Show the human, in one pass: the version, tag, branch, the approved changelog
   section, and exactly what steps 5-7 will run (per the preferences stored in
   `.release/`). One approval covers the whole block. A Preference can waive the
   gate for these ("push directly, no Go gate") — then run 5-7 straight after the
   branch.

Run in order, without further questions — every question was asked upstream and
answered once, in `.release/`:

5. Push: current branch, the tag, and the release branch.
6. GitHub release, when `config.json` has `githubReleases`: `gh release create
   <tagPrefix><version> --title <tagPrefix><version> --notes-from-tag`.
7. Publish to the package registry, per the publish target found in Survey.