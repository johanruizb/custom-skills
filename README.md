# custom-skills

Personal collection of Claude Code skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Skills

### git-commit

Fast, autonomous Conventional Commits built around the Git index and the current task context. A bash helper handles compact inspection, safe explicit staging, message validation, and commit execution.

Commits the existing staged set as authoritative. When nothing is staged, it stages only the explicit paths changed for the task. It creates one cohesive commit by default and splits only genuinely independent changes.

**Structure:**

- `SKILL.md` — Fast-path policy, cohesion rules, and safety boundaries
- `scripts/prepare_commit.sh` — Compact `inspect` mode and deterministic `commit` executor
- `references/conventional-commits.md` — Optional type and breaking-change reference

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit
```

**Usage:** Explicitly ask Claude Code to commit the current changes. The skill reuses task context, inspects only when needed, and commits the staged set or explicit task paths without rereading the entire diff.

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

### investigate-before-edit

Use before ANY code modification. Forces an investigation phase that inspects the codebase with harness tools before editing, so decisions are backed by evidence rather than assumptions. Presents a research summary and waits for confirmation on destructive or ambiguous changes.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill investigate-before-edit
```

### issue-enrichment

Use when a GitHub issue or feature request is too brief to implement and needs to be enriched with technical context from the codebase before implementation. Investigates the project, finds affected code, and rewrites the issue with the context a developer needs — without expanding scope.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill issue-enrichment
```

### pr-test-checklist

Analyze changes in one or more Pull Requests and generate a manual testing checklist for the application. Reviews the actual diff and source code to produce actionable, traceable tests free of assumptions. Does not perform full regression — only validates what changed and its direct side effects.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill pr-test-checklist
```

### prompt-enhancer

Rewrite and improve prompts to make them clear, actionable, and useful for ChatGPT, coding agents, design tools, product analysis, or any AI. Turns vague ideas, quick notes, or poorly written prompts into well-structured, ready-to-use instructions while preserving the original intent and technical terms.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill prompt-enhancer
```

### screaming-architecture-refactor

Reorganize a specific subpath of a project to Screaming Architecture + feature-based folders. Designed to run repeatedly over different paths of the same project for incremental, consistent, and safe migration.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill screaming-architecture-refactor
```

### simplify-codebase

Analyze an entire codebase for accidental complexity — duplication, unnecessary abstractions, redundant dependencies, dead code, inconsistent patterns — then propose and apply a prioritized simplification plan. Harness-agnostic: discovers available tools at runtime and adapts.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill simplify-codebase
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
- [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — inspiration for custom skills workflows (MIT)