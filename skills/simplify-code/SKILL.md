---
name: simplify-code
description: "Parallel 3-agent cleanup of an entire codebase."
version: 2.0.0
author: Hermes Agent (inspired by Claude Code /simplify)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, cleanup, refactor, delegation, subagent, parallel, simplify, codebase]
    related_skills: [codebase-audit, requesting-code-review, test-driven-development, plan]
---

# Simplify Code — Parallel Full-Codebase Review & Cleanup

Review an entire codebase with three focused reviewers running in
parallel, aggregate their findings, and apply the fixes worth applying.

**Core principle:** Three narrow reviewers beat one broad reviewer. Each one
deeply searches the codebase for a single class of problem — reuse, quality,
efficiency — without diluting its attention across all three. They run
concurrently, so you pay the latency of one review, not three.

## When to Use

Trigger this skill when the user says any of:

- "simplify" / "simplify the codebase" / "simplify this project"
- "review the codebase" / "clean up the codebase" / "clean up the project"
- "audit for over-engineering" / "reduce complexity"
- "/simplify" (if they're carrying the Claude Code habit over)

Optional modifiers the user may add — honor them:

- **Focus:** "simplify focus on efficiency" → run only the efficiency reviewer
  (or weight the aggregation toward it). Recognized focuses: `reuse`,
  `quality`, `efficiency`.
- **Dry run:** "simplify but don't change anything" / "just report" → run the
  three reviewers, present findings, apply NOTHING. Ask before applying.
- **Scope:** "simplify src/" / "simplify the auth module" / "simplify
  frontend only" → narrow the codebase scope accordingly (see Phase 2).

Do NOT auto-run this. It costs three subagents' worth of tokens scanning the
full codebase — invoke it only when the user explicitly asks.

## The Process

### Phase 1 — Project Discovery

Map the codebase before launching reviewers:

1. Find the repository root (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.).
2. Map the directory structure. Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, `migrations`, generated code, lockfiles, and binary assets.
3. Identify languages, frameworks, build tools, test runners, and linter/formatter configs from dependency manifests and config files.
4. Identify entry points, source directories, test directories, and logical module boundaries.
5. Read any project-level conventions files: `AGENTS.md`, `CLAUDE.md`, `HERMES.md`, `.editorconfig`, linter configs.

Capture the module list, source paths, test paths, and conventions as structured context for the reviewers.

### Phase 2 — Scope & Configuration

Ask the user for:

1. **Scope**: entire codebase (default), specific directories, or specific modules.
2. **Areas**: reuse, quality, efficiency, or all (default: all).
3. **Depth**: quick (surface patterns via grep/search), standard (deep read of key files per module), or exhaustive (every source file). Default: standard.
4. **Execution mode**:
   - `simplify-only` — report findings, no changes.
   - `simplify-select` — review, then user picks fixes interactively.
   - `simplify-auto` — review, then auto-fix all SAFE-tier findings.
   Default: `simplify-select`.

Present the plan (scope, modules, areas, depth, mode) for confirmation. For large codebases (>50 source files), warn the user about token cost and offer to scope down per module or area.

### Phase 3 — Launch three reviewers in parallel

Use `delegate_task` **batch mode** — pass all three tasks in one `tasks`
array so they run concurrently. Three is the right fan-out; it's well within
the `delegation.max_concurrent_children` budget on any default install.

Give **every** reviewer:

- The **full project map** (module list, source paths, entry points, conventions, language/framework info from Phase 1).
- The **scope** the user selected (entire codebase, specific dirs, or modules).
- The **depth** instruction (quick/standard/exhaustive).
- Tools: `terminal`, `file_read`, `file_search`/`grep`, `file_find`/`glob`.

Tell each reviewer to:

- **Read actual source files** — don't reason from file names or assumptions.
- **Search the full codebase** for evidence across modules (cross-file issues only show up with broad searching).
- **Apply Chesterton's Fence:** before flagging anything for removal, run
  `git blame` on the line to understand why it exists. If you can't determine
  the original purpose, mark it `confidence: low` — don't guess.
- Report findings as structured output with confidence and risk:
  ```
  file:line → problem → suggested fix | confidence: high/medium/low | risk: SAFE/CAREFUL/RISKY
  ```
  - **SAFE** = proven not to affect behavior (unused imports, commented-out
    code, dead code with zero references, pass-through wrappers). Auto-apply these.
  - **CAREFUL** = improves without changing semantics (rename local variable,
    flatten nested ternary, extract helper, consolidate dupes). Apply with test verification.
  - **RISKY** = may change behavior or breaks public contracts (N+1
    restructuring, public API rename, memory lifecycle change). Flag for
    human review — do NOT auto-apply.
- Skip nits and style-only churn. Only flag things that materially improve
  the code.

Pass these three goals (drop any the user's area selection excludes):

**Reviewer 1 — Code Reuse**
> Review this codebase for code that duplicates functionality elsewhere.
> Search the entire codebase (use file_search/grep) for existing functions,
> constants, or patterns that duplicate each other. Flag: functions defined
> in multiple places that do the same thing; hand-rolled logic that an
> existing utility already does (manual string/path manipulation, custom env
> checks, ad-hoc type guards, re-implemented parsing); near-identical modules
> or files. For each, name the definitive version to keep and where all
> duplicates live. If a duplicate exists for good reason (different
> dependency contexts, intentional fork), note it and skip.

**Reviewer 2 — Code Quality**
> Review this codebase for quality problems. Look for: redundant state
> (values that duplicate or could be derived from existing state; caches
> that don't need to exist); parameter sprawl (functions with too many params
> that should be restructured); copy-paste-with-variation (near-duplicate
> blocks that should share an abstraction); leaky abstractions (exposing
> internals, breaking encapsulation boundaries); stringly-typed code (raw
> strings where a constant/enum/registry already exists — check canonical
> registries before flagging); AI-generated slop patterns (extra comments
> restating obvious code like `// increment counter` above `count++`;
> unnecessary defensive null-checks on already-validated inputs; `as any`
> casts that bypass the type system; patterns inconsistent with the rest of
> the project). For each, give the concrete refactor.

**Reviewer 3 — Efficiency**
> Review this codebase for efficiency problems. Look for: unnecessary work
> (redundant computation, repeated file reads, duplicate API calls, N+1
> access patterns); missed concurrency (independent ops run sequentially);
> hot-path bloat (heavy/blocking work on startup or per-request paths);
> TOCTOU anti-patterns (existence pre-checks before an op instead of doing
> the op and handling the error); memory issues (unbounded growth, missing
> cleanup, listener/handle leaks); overly broad reads (loading whole files
> when a slice would do); silent failures (empty catch blocks, ignored error
> returns, `except: pass`, `.catch(() => {})` with no handling, error
> propagation gaps — these hide bugs and should at minimum log before
> swallowing). For each, give the concrete fix and why it's faster or safer.

### Phase 4 — Aggregate and apply

Wait for all three to return (batch mode returns them together).

1. **Merge** the findings into one list, deduping where reviewers overlap.
2. **Discard false positives** — you have the most context; you don't have to
   argue with a reviewer, just drop weak or wrong suggestions silently.
3. **Resolve conflicts.** Reviewers can disagree (Reviewer 1: "use existing
   util X"; Reviewer 3: "X is slow, inline it"). Default resolution order:
   **correctness > the user's stated focus > readability/reuse > micro-perf.**
   Don't apply a perf "fix" that hurts clarity unless the path is genuinely
   hot. When two suggestions are mutually exclusive and both defensible, pick
   the one that touches less code and note the alternative.
4. **Apply in risk-tier order:**
   - **SAFE first** (auto-apply): unused imports, commented-out code,
     pass-through wrappers, redundant type assertions, dead code with zero
     references. Run tests after.
   - **CAREFUL next** (apply with verification, one file at a time): rename
     locals, flatten ternaries, extract helpers, consolidate dupes. Run tests
     after each file. Revert any that break.
   - **RISKY last** (flag for review — do NOT auto-apply): N+1 restructuring,
     public API changes, concurrency fixes, error-handling changes. Present
     each with risk description and test coverage status.
   If the user opted for a dry run or `simplify-only` mode, present all three
   tiers and apply nothing.
5. **Verify** you didn't break anything: run the project's tests (targeted to
   touched files first, then broader), and re-run any linter/type check the
   repo uses. If a fix breaks a test, revert that one fix and report it.
6. **Summarize** what you changed: a short list of applied fixes grouped by
   reviewer category and risk tier, plus any findings you deliberately skipped
   and why.

### Phase 5 — Report

Generate a summary containing:

- Scope analyzed (files, modules, lines).
- Findings grouped by category (reuse/quality/efficiency) and risk tier.
- Fixes applied with file:line references.
- Findings skipped with reasons.
- Recommendations for RISKY-tier findings the user should review manually.
- Limitations (areas not covered, tools unavailable).

## Context Management for Large Codebases

- Process modules in batches, never load the entire codebase at once.
- Give reviewers the project map and scope, not every source file. They search
  and read files on demand.
- For repos >100 source files, scope down to specific modules or directories
  per run. A full-codebase simplify on a large repo should be split across
  multiple sessions, one module group at a time.
- Re-read a file before applying a fix (it may have changed).

## Pitfalls

- **Don't fan out wider than ~3.** More reviewers means more cost and more
  conflicting suggestions to reconcile, not better coverage. Three categories
  cover the space.
- **Give the FULL project map to each reviewer.** Splitting the codebase across
  reviewers defeats the design — cross-module duplication and N+1s only show up
  with the full picture.
- **Reviewers search, they don't guess.** A reuse finding with no pointer to
  the existing utility ("there's probably a helper for this") is noise. Require
  `file:line` evidence; drop findings that lack it.
- **Apply ≠ rewrite.** This is cleanup, not a license to refactor the whole
  project. Keep edits scoped to the specific problem plus the minimal
  surrounding change a fix requires.
- **Respect project conventions.** If the repo has AGENTS.md / CLAUDE.md /
  HERMES.md or a linter config, fold those rules into the reviewer prompts so
  suggestions match house style instead of fighting it.
- **Large codebases blow context.** For repos with hundreds of source files,
  scope down before delegating. Split the run into multiple sessions, one
  module group at a time.
- **Over-trusting dead code tools.** `knip`, `ts-prune`, and `depcheck` flag
  exports that ARE used dynamically (string-based imports, reflection). Always
  grep for the symbol name before removing — a clean tool report is not proof.
- **Renaming without checking public contracts.** Export names, API route
  paths, DB column names, and config keys are contracts — even if the name is
  bad, renaming breaks consumers. Tag public-contract changes as RISKY; never
  auto-rename them.
- **Removing "unnecessary" error handling.** An empty catch block or ignored
  error might be intentional — the error is expected and benign in that
  context. Flag it, don't remove it; let the human decide.
- **Not excluding generated/vendor code.** `node_modules`, `dist`, `vendor`,
  lockfiles, `migrations`, and generated code should be excluded. Analyzing
  them wastes context and produces noise.

## Restrictions

- Do NOT apply any fix without explicit user authorization (except in `simplify-auto` mode for SAFE-tier findings).
- Do NOT modify production code beyond the minimal safe fix.
- Do NOT refactor unrelated code during a fix.
- Do NOT claim tests passed if they weren't run.
- Do NOT raise findings without concrete evidence (file + line + code snippet).

## Related

If your install has the `subagent-driven-development` skill (optional), it
covers the complementary case: parallel review *during* implementation, per
task. This skill is the standalone *after-the-fact* cleanup pass. Use
`codebase-audit` for security/bug/performance-focused audits with deeper
research and version-specific analysis. Use `requesting-code-review` for the
pre-commit security/quality gate on recent changes only.
