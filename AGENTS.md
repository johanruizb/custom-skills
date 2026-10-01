# Repository Guidelines

## Project Overview

Personal collection of 15 coding-agent skills, installable via [skills.sh](https://skills.sh). Each skill is a self-contained instruction package an agent loads on demand — no application code, no runtime. Everything an agent needs lives inside one skill directory.

Install (all or one):

```bash
npx skills add johanruizb/custom-skills --global
npx skills add johanruizb/custom-skills --skill git-commit --global
```

## Architecture & Data Flow

No build, no bundling. The unit of work is the skill directory; the unit of change is one skill's files.

```
repo/<skill>/SKILL.md            # the instruction surface an agent executes
repo/<skill>/references/*.md     # disclosed reference reached by pointer from SKILL.md
repo/<skill>/templates/          # output skeletons the skill fills or copies
repo/<skill>/scripts/*.py        # optional helper tools the agent runs directly
```

Flow: skills.sh installs the directory into a runtime's skill root (`~/.agents/skills/`, `~/.claude/skills/`) → the agent's skill router matches the frontmatter `description` against the task → loads `SKILL.md` → follows its instructions, reading `references/` or running `scripts/` only when the text points there.

Architecture pattern inside heavy skills (code-health, web-perf-tuning, init-deep): **Core + Adapters**. The `SKILL.md` core is written in harness-neutral capability terms (`file_read`, `cmd_exec`, `state_persist`); per-harness behavior lives in `references/harness-adapters.md`. Keep that split when adding skills: core logic must never name a specific tool.

Cross-skill relationships are declared in frontmatter as `related_skills`, never by file imports. One intentional duplication exists — `code-health/references/harness-adapters.md` and `test-suite-improver/references/harness-adapters.md` are near-copies, each carrying a sync-notice header. If you edit one, update both.

## Key Directories

| Directory | Role |
|---|---|
| `git-commit/` | Conventional Commits from task context + staged index |
| `code-health/` | Whole-codebase audit + simplification, merged from former `codebase-audit` + `simplify-codebase` |
| `test-suite-improver/` | Test suite audit and rewrite |
| `web-perf-tuning/` | Performance loop; per-stack playbooks in `references/<stack>.md` |
| `investigate-before-edit/` | Pre-edit investigation discipline; real-case pitfalls in `references/` |
| `code-documentation/`, `issue-enrichment/`, `release-to-github/`, `pr-test-checklist/`, `screaming-architecture-refactor/`, `prompt-enhancer/`, `init-deep/`, `anglicize-repo/`, `visual-feedback-loop/`, `fork-pr/` | One-purpose instruction skills |

Root files: `README.md` (skill catalog), `LICENSE` (MIT), `.gitignore` (ignores `.omc/`, `dist/`, `.commandcode`, `.serena/`).

## Development Commands

No build/test/lint commands exist — this is a Markdown-only repo. Verification is reading and running the material:

```bash
npx skills add johanruizb/custom-skills --skill <name> --global   # install a changed skill
git log --oneline -12                                            # history conventions
```

## Code Conventions & Common Patterns

**Frontmatter (SKILL.md):** every skill starts with `---`-delimited YAML. Required: `name` — must equal the directory name verbatim (invariant held across all 14) — and `description` in English, model-facing, listing the distinct trigger branches, including Spanish trigger phrases when users speak Spanish to that skill. Always `license: MIT`. Optional: `allowed-tools` (restricting tool surface — git-commit, anglicize-repo, release-to-github use it), `metadata: {author, version, platforms, hermes: {tags, related_skills}}` with bump-worthy semantic version.

**Body structure** (recurring across the collection): `# <skill name>` → `## Overview` → `## When to Use` (trigger branches; plus a "Don't use when…" exclusion) → numbered `## Phase N: <Name>` steps, each ending in an explicit **Completion criterion** → `## Common Pitfalls` → `## Verification/Completion Checklist`. Long bodies (200–350 lines) push per-case material into `references/` files pointed at from the step that needs it; the SKILL.md body stays the ordered path.

**Language:** all skill bodies and root docs in English. Spanish appears only inside trigger phrase lists (`description`, When-to-Use) — that is intentional reachability, not drift.

**Commits:** Conventional Commits, `type(scope): imperative summary`, scope = skill name (`feat(visual-feedback-loop): …`, `refactor(skills): …`, `chore: …`). One commit per cohesive change; independent skills are separate commits. Never rewrite git history.

**Docstrings/comments:** this repo's own convention is English-only, minimal inline comments.

## Important Files

- `<skill>/SKILL.md` — the executable spec; edit this first for behavior changes.
- `code-health/references/harness-adapters.md` + `test-suite-improver/references/harness-adapters.md` — paired copies, keep in sync.
- `README.md` — public catalog; every skill change that alters purpose or structure includes a README entry update.
- `.git/config` — remote `git@github.com:johanruizb/custom-skills.git`, branch `master`.

## Runtime/Tooling Preferences

- Install tooling requires Node ≥ 18 (for `npx skills`); skills themselves need only a Markdown reader.
- Scripts are plain Python 3, stdlib-only, executable directly (`python3 <skill>/scripts/<file>.py`); no dependencies, no packaging.
- No CI configured; publishing is manual `git`/skills.sh flow.
- Distribution is stateless: no sync or watch mechanism links repo and installed copies. After changing a skill, reinstall it or copy the directory into the runtime skill root before testing.

## Testing & QA

No test suite, no linter, no CI — nothing automated runs here. Change-verification is behavioral: after editing a skill, read the changed SKILL.md top-to-bottom, confirm the frontmatter parses and `name == directory`, check every `references/…` path it mentions exists, reinstall via `npx skills`, and run the skill on a real task to observe the behavior change. A skill edit with no observed run is unverified.