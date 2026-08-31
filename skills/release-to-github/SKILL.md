---
name: release-to-github
description: Cut a standardized release for the current repository — bump the version, write the changelog, commit and tag. Invoke with /release-to-github.
license: MIT
disable-model-invocation: true
allowed-tools:
  - Bash(git:*)
  - Bash(bash:*)
  - Read
  - Edit
---

# release-to-github

Cut a release from the commits since the last tag: version, changelog, release commit, tag.
Every convention is read from the repository, never assumed — that is what makes one skill
fit many projects. The steps the human cannot undo (push, GitHub release, package publish)
run last, after they have seen the release notes.

## Survey

Read the conventions before writing anything:

- Version file: `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `VERSION`.
  Fall back to `git grep` for the last tag's number.
- Changelog: `CHANGELOG.md` at the root. Offer to create it when missing.
- Commit style: `git log` since the last tag. Fall back to Conventional Commits.
- Tag style: `git tag`. Default `v`-prefixed SemVer (`v1.4.2`).
- Publish target: release workflow in `.github/workflows`, `publishConfig`, package
  registry config. Local-only when none is found.
- Release tooling: an existing `npm version` / `cargo release` / script. When present,
  run it and skip the manual bump.

Done when each convention traces to a file or `git` output, and you can name the bump
mechanism you will use (tool, or manual edit).

## Version

List the commits since the last tag (`git describe --tags --abbrev=0`), then derive the
bump from those commits:

- `fix` → patch; `feat` → minor; `!` or a `BREAKING CHANGE` footer → major.
- On `0.x`: breaking bumps minor, `feat` bumps patch.
- Non-conventional commits: read their diffs and classify by user impact.

Propose the next version with the reason (`feat` present → minor). Done when the human
has approved the number and the commit list carries no surprises (unexpected merges,
commits that belong to another branch).

## Changelog

One new section under the released version and today's date — new entries, not a rewrite:

```markdown
## [1.5.0] - 2026-08-31

### Added
### Changed
### Fixed
### Removed
### Security
```

- Drop headings with no entries.
- Phrase each entry for the user of the project, not for the committer: what changed
  in behavior, not which commit did it.
- Cover every user-facing change since the last tag. Internal chores, CI and docs
  commits may be omitted; that omission is itself a check you ran, not an oversight.
- Link the comparison with the previous tag when the file uses link references.

## Ship

1. Commit the version file(s) and the changelog together:
   `chore(release): v<version>`.
2. Tag: annotated, message equal to one summary line of the new changelog section.
3. Show the human the version, tag, and changelog section. Push (`git push` and
   `git push --tags`), create a GitHub release when the repo uses them, and publish
   to the package registry only after approval — each step separately, since none is
   reversible.