---
name: code-health
description: "Use when the user wants a deep audit or cleanup of an entire codebase: performance, bugs, security, duplication, dead code, unnecessary abstractions, or complexity. Analyzes all source code (not just diffs), discovers available tools at runtime, adapts to any harness, and optionally fixes selected findings with validation."
license: MIT
metadata:
  author: Hermes Agent
  version: "2.0.0"
  hermes:
    tags: [audit, cleanup, performance, bugs, security, deduplication, dead-code, complexity, harness-agnostic]
    related_skills: [test-suite-improver, investigate-before-edit]
---

# Code Health Audit

Deep audit of an entire codebase. Reviews all source code, not just diffs or recent changes. Harness-agnostic: discovers available tools at runtime and adapts. Finds defects (bugs, security, performance) and accidental complexity (duplication, unnecessary abstractions, dead code, inconsistent patterns), then optionally fixes selected findings with validation.

## When to Use

- User asks to audit, review, or find bugs, security issues, or performance problems in a whole codebase.
- User asks to simplify, reduce complexity, deduplicate code, or remove dead code project-wide.
- User wants a codebase health check before a release, migration, or refactoring.
- User wants a comprehensive map of the codebase's modules, dependencies, and complexity hotspots.

Don't use for:
- Reviewing only recent git changes. Use a diff-based code review instead.
- Debugging a specific known bug. Investigate and fix it directly instead.
- Documenting code (docstrings, comments). Use `code-documentation` instead.
- Architecture-level refactoring decisions. Use an architecture/design workflow instead.

## Architecture: Core + Adapters

**Core logic** (this file): discovery, planning, analysis methodology, finding format, consolidation, fix application, validation, reporting. Written entirely in terms of *capabilities*, never tool names.

**Harness adapter** (`references/harness-adapters.md`): maps every capability (file_read, file_search, cmd_exec, user_ask, subagent_spawn, ...) to the concrete tools of the detected harness (Hermes, Claude Code, OpenCode, or generic fallback). Classify each capability as available or missing in Phase 1; missing capabilities become logged limitations, never assumptions.

## Phase 1: Tool Discovery & Adapter Selection

1. Select the matching harness adapter from `references/harness-adapters.md`; no match means the generic adapter (it probes per capability).
2. For each capability, classify: available (with concrete tool name) or missing (with impact noted). Record the capability map.
3. **Completion criterion**: every capability is classified as available or missing.

## Phase 2: Project Discovery

1. Find the repository root (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `requirements.txt`, `composer.json`, etc.).
2. Map the directory structure using `file_find` and `dir_list`. Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, and any user-specified exclusions.
3. Identify languages, frameworks, build tools, test runners, and infrastructure from config files and dependency manifests. Read lockfiles and record exact versions. Do NOT assume a stack from file extensions.
4. Read project conventions: AGENTS.md, CLAUDE.md, .cursorrules, README, contributing guides, lint configs. These encode rules the fixes must respect.
5. Identify entry points, test directories, config directories, and documentation.
6. Record validation commands: test runner, linter, type checker, build command. You will need these after every change.
7. Divide the codebase into analyzable modules based on directory structure and logical boundaries.
8. **Completion criterion**: a structured project map exists with technologies, versions, module list, entry points, test setup, validation commands, and exclusion list.

## Phase 3: Planning & User Configuration

Ask the user for (ask mechanism from the harness adapter; fallback to conversation):

1. **Focus areas**: bugs, security, performance, and/or simplification (duplication, dead code, unnecessary abstractions, inconsistent patterns, redundant dependencies, complex flows). Default: all.
2. **Scope**: entire repo, specific folders, or specific modules. Default: entire repo.
3. **Exclusions**: additional paths to exclude beyond auto-detected ones.
4. **Depth**: quick (surface patterns), standard (module-by-module deep read), or exhaustive (every file + dependency analysis). Default: standard.
5. **HTML report**: yes/no. Default: no.
6. **Execution mode**:
   - `audit-only`: report findings, no changes.
   - `audit-select`: audit, then user picks fixes interactively.
   - `audit-auto`: audit, then auto-fix all findings classified as safe.
   Default: `audit-select`.
7. **Subagents**: use subagent parallelism if available. Default: yes when available.

Present the plan (scope, modules, order, tools, subagent strategy, exclusions, limitations) to the user for confirmation (same ask mechanism).

**Completion criterion**: user has confirmed focus areas, scope, mode, depth, and the plan is recorded.

## Phase 4: Technical Research

For each detected technology + version:

1. Use `web_search` and `web_extract` to consult:
   - Official documentation for the detected framework/library versions.
   - Security advisories (CVEs, GHSA, vendor advisories).
   - Known bugs and breaking changes for the exact versions in use.
   - Current best practices for the detected stack.
2. Build a temporary knowledge base of version-specific risks and recommendations.
3. Record all sources consulted.
4. If `web_search` is unavailable: note the limitation, reduce confidence on findings that depend on current external data, and rely on static analysis + known patterns.
5. **Completion criterion**: a version-specific risk profile exists for each major technology in the project, with sources cited.

## Phase 5: Audit

Use the analysis checklists from `references/analysis-checklists.md` for each selected area.

Process the codebase module by module (or in batches for large repos).

**VERIFY everything in the code.** Do not assume how something works based on naming, conventions, or training data. Read the actual files. Search for actual references. Trace actual call paths. No speculation: do not raise a finding you cannot point to in code. Mark uncertain items as `hypothesis` with `confidence: low`.

1. **Per module**: read source files, search for anti-patterns, run available linters/static analyzers via `cmd_exec`, cross-reference with the version-specific risk profile from Phase 4.
2. **Global searches**: use `file_search` to find recurring patterns across the codebase (e.g., `eval(`, `innerHTML`, SQL string concatenation, `console.log` in production, `except:`, `catch(Exception`; for simplification: copy-pasted blocks, wrappers that only delegate, symbols referenced nowhere).
3. **Static analysis**: run any available tools, eslint, pylint, bandit, semgrep, go vet, cargo clippy, npm audit, safety, etc., via `cmd_exec`. Record results. For duplication leads, pre-screen with `scripts/detect-duplicates.py`; treat output as leads to verify, not findings.
4. **Record each finding** in the Finding Format below with its evidence, then mark confidence accordingly.
5. **Tracking**: use `task_manage` to track which modules are analyzed vs pending. For large repos, write intermediate results to a state file via `state_persist`.
6. **Completion criterion**: every module in scope has been reviewed, all findings recorded with evidence, task list shows no pending modules.

### Subagent Strategy (Phase 5)

When subagents are available, split Phase 5 work by area or module:

| Subagent | Task | Input | Output |
|---|---|---|---|
| Area analyst (per area) | One focus area (performance, bugs, security, simplification) | Project map + version risk profile + analysis checklists + finding format | Structured findings |
| Module analyst (per module) | Full audit of a module subset | Module list + project map + analysis checklists + finding format | Structured findings |
| Duplication detector | Cross-module duplication search | All module paths + finding format | Duplication findings |
| Dead code hunter | Dead code search with reference verification (all reference types, not just imports) | All source paths + finding format | Dead code findings |
| Consolidator | Deduplicate, verify, rank findings | All subagent outputs | Consolidated finding list |

Each subagent returns structured findings only (no edits, no plans). Every finding must cite file:line, so the consolidator can verify it.

**Pitfall**: Subagents can modify files as collateral damage. After all subagents return, run the project's diff/status check (`git diff --stat HEAD`, `git status --short` when git is available) and revert any unintended changes.

The main agent: consolidates, deduplicates, verifies evidence, resolves contradictions. When subagents are NOT available: simulate the same separation by processing areas/modules sequentially within one agent, using the same input/output formats.

## Phase 6: Consolidation

1. Gather all findings from all agents/analyses.
2. Deduplicate: same issue found in same location is one finding. Resolve contradictions: the side whose evidence shows dynamic usage wins. Group findings that share a root cause.
3. Verify evidence: re-read the referenced code to confirm it still matches (files may have changed).
4. Assign for each finding:
   - **Severity**: critical, high, medium, low, info.
   - **Confidence**: confirmed (verified in code), probable (strong evidence), hypothesis (needs validation).
   - **Priority**: P0 (fix now), P1 (fix soon), P2 (fix when convenient), P3 (optional improvement).
   - **Fix risk**: SAFE (provably affects no behavior: dead code with zero verified references, unused imports) / CAREFUL (improves behavior-neutral code, needs test verification) / RISKY (may change behavior or break contracts, needs explicit user confirmation first).
5. Determine dependency ordering between findings (e.g., fix A before B because B depends on A). Rank the fix order: highest priority first, RISKY last.
6. **Completion criterion**: a deduplicated, verified, priority-ranked finding list with no unverified evidence.

## Phase 7: Report

Generate a report containing:

- Executive summary (counts by category/severity, top risks).
- Technologies and exact versions detected.
- Tools used and tools that were unavailable (with impact).
- Scope: files/modules analyzed, files/modules omitted.
- Findings grouped by category, each with full structured format.
- For simplification work: complexity hotspots (modules with most findings, deepest call chains, most duplication).
- Recommended resolution order.
- Audit limitations (missing tools, unverified hypotheses, areas not covered).

Present the report to the user. Structure it per `templates/code-health-report.md`. If HTML report was requested and `file_write` is available, generate it (see `references/html-report.md` and `scripts/generate-html-report.py`).

**Completion criterion**: user has received the full report (inline or HTML or both).

## Finding Format

Every finding (audit or simplification) uses the field list, enums, and worked examples defined in `references/finding-schema.md`. That file extends `category` with the simplification values (`duplication`, `abstract-cruft`, `dead-code`, `inconsistency`, `complex-flow`) and shows example findings with `PERF-`, `BUG-`, `SEC-`, and `SIMPL-` IDs. Give the schema file path to every analysis subagent.

Two rules bind on top of the schema:
- Severity grades impact; confidence grades evidence. Fix order ranks by priority first, fix risk last (RISKY only after explicit user confirmation).
- Dead-code claims of `confirmed` require verification across all reference types (imports, dynamic imports, string references, framework registers, tests, build configs). Unverifiable references cap the confidence at `hypothesis`.

## Selection of Fixes

After presenting the report, ask the user which findings to fix (same ask mechanism). Offer selection by:

- Individual finding ID.
- Category (all performance, all bugs, all security, all simplification).
- Severity (all critical, all high).
- Confidence (all confirmed).
- Module (all findings in module X).
- All safe fixes (confidence=confirmed, fix_risk=low).
- Exclude specific IDs.
- Audit-only (no fixes).

## Phase 8: Fix Application

For each selected finding:

1. Re-read the current code at the finding location (it may have changed since audit).
2. Analyze impact: what else depends on this code? Search for references. For renaming/removals, update every call site and any string/dynamic references.
3. Check `source` references for correct fix approach if version-specific.
4. Plan the minimal, safe change. Do NOT refactor unrelated code. When consolidating duplication or removing a pass-through, the change must beat the deletion test: inlining must leave the code simpler than the layer it replaced.
5. Apply the change using `file_write` / file editing tools.
6. Respect project conventions, style, and architecture detected in Phase 2. A consistent project pattern is a convention even if it looks unconventional. Flag only genuine inconsistency within the project.
7. Run validation after each batch of 1-5 related changes, not just at the end: fastest check first (lint, typecheck), then the relevant test subset. If a change breaks tests, revert that specific change, record the regression, and move to the next independent change.
8. Record: what was changed, which finding it resolves, the diff.
9. Review the generated diff; revert or adjust changes with unexpected side effects.
10. **Completion criterion**: each selected finding has a recorded fix with diff, or a documented reason it was skipped.

## Phase 9: Validation

After fixes, run all available checks via `cmd_exec`:

1. Test suite (project's test runner).
2. Linters (project's linter config).
3. Type checkers (tsc, mypy, etc.).
4. Static analyzers.
5. Security scanners.
6. Build/compile.
7. App startup smoke test (when reasonable).
8. Targeted regression tests for modified areas.

For projects whose test suite needs seeded data, write a focused script that imports the app and asserts each fix.

Classify validation result as one of:

- **passed**: all checks ran and passed.
- **failed**: one or more checks ran and failed.
- **partial**: some checks passed, some could not run.
- **not_run**: validation could not execute (missing tools, missing test setup).
- **impossible**: environment cannot support validation.

**Completion criterion:** validation result is classified and all executed check results are recorded.

## State & Resumption

When `state_persist` is available, persist audit state to `.code-health-state.json` after each phase (schema and field meanings in `templates/code-health-state.json`): configuration, capability map, project map, modules analyzed/pending, findings with status, fixes applied, validation results, sources consulted, limitations. This enables resuming an interrupted run without re-analyzing completed modules.

When `state_persist` is unavailable: keep findings in context and track progress via `task_manage`. Resumption is limited.

## Context Management for Large Repos

- Process modules in batches; write intermediate findings to state after each batch; drop raw code from context once a module summary exists.
- Prioritize: entry points, auth, data access, config > utility files, tests, docs.
- Re-read a file before applying a fix (it may have changed). Invalidate a module's findings if its files changed after analysis.
- Use subagents to parallelize and keep each agent's context focused.

## Restrictions

- Do NOT apply any change without explicit user authorization. `audit-auto` is the only exception: it auto-fixes only confidence=confirmed AND fix_risk=low findings.
- Do NOT modify production code beyond the minimal safe fix for a confirmed finding.
- Do NOT claim validation passed if it was not executed.
- Do NOT assume tools, commands, or frameworks exist before inspecting the project.
- Do NOT load the entire codebase into context for repos >50 files.
- Do NOT skip the version-specific research phase. A fix valid for one version may break another.
