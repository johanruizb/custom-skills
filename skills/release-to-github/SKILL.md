---
name: release-to-github
description: "Cut a standardized release for the current repository: bump the version, write the changelog, commit, tag, and branch."
license: MIT
disable-model-invocation: true
allowed-tools:
  - Bash(bash:*)
  - Read
  - Edit
---

# release-to-github

Cut a release from the commits since the last tag: version, changelog, release commit,
tag, and a version branch.

Every convention comes from the repository, because one skill serves many projects. The
human cannot undo a push, a GitHub release, or a package publish, so those run last,
after they have seen the release notes.

## Survey

Read the conventions before writing anything:

- Version file: `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `VERSION`.
  Fall back to `git grep` for the last tag's number.
- Changelog: `CHANGELOG.md` at the root. Offer to create it when missing.
- Commit style: `git log` since the last tag. Fall back to Conventional Commits.
- Tag style: `git tag`. Default `v`-prefixed SemVer (`v1.4.2`).
- Release branch: existing `release/*` branches (`git branch -r`). Each release gets a
  branch named `release/v<version>` at the release commit.
- Publish target: release workflow in `.github/workflows`, `publishConfig`, package
  registry config. Local-only when none is found.
- Release tooling: an existing `npm version` / `cargo release` / script. When present,
  run it and skip the manual bump. Note whether it also commits and tags; if it does,
  Ship skips those steps too.

Pre-flight checks, before any write:

- Working tree clean (`git status --porcelain`).
- No prior tag with the next version; no existing `release/v<version>` branch.
- `gh auth status` passes when the repo has a GitHub release workflow or the human wants
  a GitHub release.
- No previous tag at all: a first release. The commit range starts at the root commit,
  the changelog omits the full-changelog line, and Version classifies every commit.

Done when each convention traces to a file or `git` output, you can name the bump
mechanism you will use (tool, or manual edit), and every pre-flight check passes or has
a decision from the human.

## Version

List the commits since the last tag (`git describe --tags --abbrev=0`; on a first
release, the root commit), then derive the bump from those commits:

- `fix` → patch; `feat` → minor; `!` or a `BREAKING CHANGE` footer → major.
- On `0.x`: breaking bumps minor, `feat` bumps patch.
- Non-conventional commits: read their diffs and classify by user impact.

Propose the next version with the reason (`feat` present → minor). Done when the human
has approved the number and the commit list carries no surprises (unexpected merges,
commits that belong to another branch).

## Changelog

One new section under the released version and today's date. Write new entries; never
rewrite old sections:

```markdown
## [1.5.0] - 2026-08-31

### Added
### Changed
### Fixed
### Removed
### Deprecated
### Security
```

- Drop headings with no entries.
- Write every entry through the unslop skill, and re-run it on any later revision of
  the section.
- Phrase each entry for the user of the project, not for the committer: what changed
  in behavior, not which commit did it.
- End the section with a full-changelog line, unless this is the first release:
  `**Full changelog:** https://github.com/<owner>/<repo>/compare/vA...vB`. Build it from
  the previous tag, the new one, and `git remote get-url origin`. When the file keeps its
  links in a reference block at the bottom, put the URL there instead of inline.

Done when every user-facing change since the last tag has an entry, and every omission
(internal chores, CI, docs) was decided, not missed.

## Ship

When the release tooling already committed and tagged (see Survey), skip steps 1-2.

1. Commit the version file(s) and the changelog together:
   `chore(release): v<version>`.
2. Tag: annotated, first changelog entry as the subject, the whole new section as the
   body (`git tag -a v<version> -m "<subject>" -m "<body>"`).
3. Branch: `release/v<version>` pointing at the release commit, so every version keeps
   a branch to backport fixes onto. Reuse the prefix only when one already exists in the
   repo; default to `release/`.

Then one approval per step, in this order. Nothing irreversible runs before its
approval:

4. Show the human the version, tag, branch, and changelog section.
5. Push: current branch, the tag, and the release branch.
6. GitHub release, when the repo uses them:
   `gh release create v<version> --title v<version> --notes-from-tag`.
7. Publish to the package registry, per the publish target found in Survey.