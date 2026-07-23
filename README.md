# custom-skills

Personal collection of Claude Code skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Skills

### git-commit

Standardized git commits using Conventional Commits with autonomous message generation. A bash script handles mechanical data collection (diff, status, log, secret detection, type hints); the LLM handles semantic decisions (grouping, type, message).

Auto-detects commit type and scope from changes, commits autonomously without confirmation prompts, and splits changes into atomic commits grouped by logical type/scope. Operates on the current working directory.

**Structure:**

- `SKILL.md` — Workflow rules and safety protocol
- `scripts/prepare_commit.sh` — Data collection (diff, status, log, secret scan, type hints)
- `references/conventional-commits.md` — Type table, format, breaking changes reference

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit
```

**Usage:** Run the skill from Claude Code's command input. It will run the data collection script, analyze the output, group changes into atomic commits, and commit each group with a conventional commit message.

### deep-interview

Structured Socratic requirements interview for vague ideas before planning or implementation.

Asks one targeted question at a time, scores ambiguity across weighted clarity dimensions, confirms the top-level scope, inspects brownfield code before asking repository questions, and produces a pending-approval specification before any execution.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill deep-interview
```

**Usage:** Run the skill when a request is vague or high-risk, for example "deep interview this feature idea", "interview me before coding", or "no quiero que asumas". It will clarify requirements and generate a spec before implementation.

### code-documentation

Generate, update, or regenerate inline documentation (docstrings, JSDoc, comments) across a codebase. Analyzes project structure, detects language/framework conventions, offers incremental or full-regeneration modes, and validates that docs match the code without changing behavior.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill code-documentation
```

### codebase-audit

Deep audit of an entire codebase for performance, bugs, and/or security issues. Reviews all source code (not just diffs), discovers available tools at runtime, adapts to any harness, and optionally fixes selected findings.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill codebase-audit
```

### init-deep

Deep repository-context initialization. Analyzes the repository and generates or updates a useful hierarchy of `AGENTS.md` files for coding agents based on actual repository architecture and conventions. 

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill init-deep
```

### screaming-architecture-refactor

Reorganize a specific subpath of a project to Screaming Architecture + feature-based folders. Designed to run repeatedly over different paths of the same project for incremental, consistent, and safe migration.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill screaming-architecture-refactor
```

### test-suite-improver

Audit a project's test suite, evaluate the quality of every existing test, then improve the suite by writing valuable tests, fixing broken ones, and removing ones that add no value. Harness-agnostic.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill test-suite-improver
```

## Requirements

- Node.js >= 18 (for `npx skills`)
- Git

## Credits

- [github/awesome-copilot](https://github.com/github/awesome-copilot) — original git-commit skill (MIT)
- [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — inspiration for deep-interview (MIT)
