---
name: code-health
description: "Use when the user wants a deep audit or cleanup of an entire codebase: performance, bugs, security, duplication, dead code, unnecessary abstractions, or complexity. Analyzes all source code (not just diffs), discovers available tools at runtime, adapts to any harness, and optionally applies selected fixes with validation in an isolated git worktree."
license: MIT
metadata:
  author: Hermes Agent
  version: "2.2.2"
  hermes:
    tags: [audit, cleanup, performance, bugs, security, deduplication, dead-code, complexity, worktree, harness-agnostic]
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

## User Questions

Every `user_ask` call uses one entry from `references/user-questions.md`: the exact question text, header, options, order, selection mode, and default. A bare prompt, an empty call, or invented/merged options is a protocol failure. One question carries one decision; never combine settings.

Record canonical values (not labels) in state and reuse recorded answers on resume. If the harness has no structured ask tool, present the same catalog entry in conversation (options as a numbered list, free text as the exact prompt) and require a canonical value; do not paraphrase it.

## Phase 1: Tool Discovery & Adapter Selection

1. Select the matching harness adapter from `references/harness-adapters.md`; no match means the generic adapter (it probes per capability).
2. For each capability, classify: available (with concrete tool name) or missing (with impact noted). Record the capability map.
3. **Completion criterion**: every capability is classified as available or missing.

## Phase 2: Project Discovery

1. Find the repository root (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `requirements.txt`, `composer.json`, etc.).
2. When git is available, record the current branch, HEAD commit, working-tree cleanliness (`git status --porcelain`), and `git worktree list --porcelain`; these drive worktree isolation before Phase 8.
3. Map the directory structure using `file_find` and `dir_list`. Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, and any user-specified exclusions.
4. Identify languages, frameworks, build tools, test runners, and infrastructure from config files and dependency manifests. Read lockfiles and record exact versions. Do NOT assume a stack from file extensions.
5. Read project conventions: AGENTS.md, CLAUDE.md, .cursorrules, README, contributing guides, lint configs. These encode rules the fixes must respect.
6. Identify entry points, test directories, config directories, and documentation.
7. Record validation commands: test runner, linter, type checker, build command. You will need these after every change.
8. Divide the codebase into analyzable modules based on directory structure and logical boundaries.
9. **Completion criterion**: a structured project map exists with technologies, versions, module list, entry points, test setup, validation commands, exclusion list, and VCS isolation facts.

## Phase 3: Planning & User Configuration

Ask the setup questions from `references/user-questions.md` in catalog order: `focus_areas`, `scope`, `exclusions`, `depth`, `html_report`, `execution_mode`, `subagents`, `isolation`. Use the catalog's exact text, options, order, and defaults. Record canonical values in `config` and `isolation`.

`isolation` is conditional: record `worktree` without asking when git worktree is available and the primary tree is clean; ask the catalog question only when that default is unavailable or the user requests a change. If `execution_mode=audit-only`, record `isolation.strategy=none` without asking. When a capability is missing (`subagent_spawn` or `file_write`), record the catalog's fallback and log the limitation; do not ask a question the harness cannot act on.

Present the plan (scope, modules, order, tools, subagent strategy, isolation, exclusions, limitations) and ask `plan_confirmation` from the catalog. If the answer is `adjust_scope`, `adjust_areas`, `adjust_mode`, or `adjust_isolation`, re-ask the listed questions, update the plan, and ask `plan_confirmation` again. Only `proceed` starts the audit.

**Completion criterion**: every setup answer is recorded with a canonical value, `plan_confirmation=proceed`, and the plan is recorded; `cancel` ends the run without auditing.

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

**Pitfall**: Subagents can modify files as collateral damage. Record `git status --porcelain` before spawning them, then compare after; restore only paths that changed during the subagent run, never pre-existing user changes.

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

After presenting the report: if `config.mode=audit-only`, record `answers.fix_selection_method=audit_only` and skip fixes; if `config.mode=audit-auto`, record `answers.fix_selection_method=all_safe` and use the confirmed SAFE findings; otherwise ask `fix_selection` from `references/user-questions.md`. When the chosen method has a follow-up, ask that catalog entry next and resolve the answer to concrete finding IDs. Any selection that resolves to a RISKY finding requires `risky_confirmation` from the catalog before Phase 8. Record the method and resolved IDs in `answers`.

**Completion criterion**: every selected fix maps to a finding ID, the method and details are recorded in `answers`, or `audit_only`/`cancel` is recorded.

## Worktree Isolation

Audit-only runs skip this section; a worktree exists only when at least one fix is selected. Fix runs use a dedicated worktree by default and never touch the user's checked-out branch. Only an explicit `isolation=in-place` or `fix_blocked=in_place` choice permits editing the primary worktree. Create one linked worktree on a new branch from the audited commit, and treat it as the fix workspace.

**Branch standard**: every worktree branch is `code-health/audit-<mode>-<YYYYMMDD-HHMMSS>` (UTC), e.g. `code-health/audit-security-20261017-153045`; it matches `^code-health/audit-(all|bugs|performance|security|simplification|mixed)-[0-9]{8}-[0-9]{6}(-[0-9]+)?$`. `<mode>` mirrors the configured focus areas: `bugs`, `security`, `performance`, or `simplification` for one area, `all` for all four, and `mixed` for any other combination. The branch carries the fixed `code-health/audit-` prefix, the mode, and the UTC timestamp; a collision suffix is the only allowed addition. Only an explicit user-provided name replaces this pattern. If the branch or worktree path exists, append `-2`, `-3`, ... to the timestamp. Validate with `git check-ref-format --branch <branch>` before creating the worktree.

1. **Preflight**: base the worktree on the audited HEAD. The primary worktree must have no uncommitted source changes; exclude only the skill's own `.code-health-state.json` from the check. If it is otherwise dirty, stop before editing and ask `fix_blocked` from `references/user-questions.md` with the reason. On `resolve`, wait for the user to clean the tree, then re-run preflight; on `in_place` or `audit_only`, record the choice and proceed. Never stash, reset, checkout, or commit the user's existing changes to make the tree clean. A worktree contains tracked files only: if the audited code or its environment depends on untracked or ignored files, ask `fix_blocked` with that reason; `resolve` means the user provides the missing files before retrying.
2. **Create**: pick a writable sibling path outside the repository (e.g. `<repo-parent>/<repo-name>-code-health-audit-<mode>-<timestamp>`); if no writable parent exists, ask `fix_blocked`. Run `git worktree add -b <branch> <path> <base-commit>` with the branch from the standard above. Base on the audited HEAD unless the user names another ref; fetch before using a remote ref. Never reuse a branch checked out in another worktree and never switch branches in the primary worktree.
3. **Verify**: `git -C <path> rev-parse --show-toplevel` resolves to `<path>`, `git -C <path> branch --show-current` equals `<branch>`, and the primary worktree's `git status --porcelain` shows no new source changes (state file excepted).
4. **Use**: run all fix edits, re-reads, diffs, and validation commands with the worktree as the working directory. Give applying subagents the worktree path, or the primary root when `in-place` is recorded; never mix paths within one run.
5. **Record** in state: strategy (`worktree`, `in-place`, or `none`), path, branch, base ref and commit, status.
6. **Completion criterion**: a dedicated worktree exists on a new branch at the audited commit that matches the branch standard (or the user's exact branch name), the verification commands pass, and the primary worktree has no new source changes; or an explicit `in-place`/`audit-only` fallback is recorded.

If git or `cmd_exec` is unavailable, or worktree creation fails, ask `fix_blocked` from `references/user-questions.md` with the reason. `resolve` means retry after the blocker is fixed; `in_place` and `audit_only` record the corresponding strategy. Do not edit silently.

## Phase 8: Fix Application

For each selected finding:

1. Establish worktree isolation (see Worktree Isolation) before the first edit; record the worktree path and branch, or the approved `in-place`/`audit-only` fallback.
2. Re-read the current code at the finding location in the recorded fix workspace (it may have changed since audit).
3. Analyze impact: what else depends on this code? Search for references. For renaming/removals, update every call site and any string/dynamic references.
4. Check `source` references for correct fix approach if version-specific.
5. Plan the minimal, safe change. Do NOT refactor unrelated code. When consolidating duplication or removing a pass-through, the change must beat the deletion test: inlining must leave the code simpler than the layer it replaced.
6. Apply the change using `file_write` / file editing tools.
7. Respect project conventions, style, and architecture detected in Phase 2. A consistent project pattern is a convention even if it looks unconventional. Flag only genuine inconsistency within the project.
8. Run validation in the recorded fix workspace after each batch of 1-5 related changes, not just at the end: fastest check first (lint, typecheck), then the relevant test subset. If a change breaks tests, revert that specific change, record the regression, and move to the next independent change.
9. Record: what was changed, which finding it resolves, the diff.
10. Review the diff in the recorded fix workspace (`git -C <path> diff`, or `git diff` in-place); revert or adjust changes with unexpected side effects.
11. **Completion criterion**: each selected finding has a recorded fix with diff, or a documented reason it was skipped; every fix lives in the isolated worktree, or in the primary tree only under an explicit `isolation=in-place` or `fix_blocked=in_place` approval.

## Phase 9: Validation

After fixes, run all available checks via `cmd_exec` in the recorded fix workspace: the worktree path, or the primary root under an explicit `in-place` approval. Use that path as the working directory:

1. Test suite (project's test runner).
2. Linters (project's linter config).
3. Type checkers (tsc, mypy, etc.).
4. Static analyzers.
5. Security scanners.
6. Build/compile.
7. App startup smoke test (when reasonable).
8. Targeted regression tests for modified areas.

For projects whose test suite needs seeded data, write a focused script that imports the app and asserts each fix.

A fresh worktree may lack installed dependencies, build caches, and local env files. Run the project's documented setup/install step there first. If the environment cannot be reproduced, classify validation `partial` or `impossible`, list what the user must run, and do not validate against the primary worktree unless `in-place` is the recorded strategy.

Classify validation result as one of:

- **passed**: all checks ran and passed.
- **failed**: one or more checks ran and failed.
- **partial**: some checks passed, some could not run.
- **not_run**: validation could not execute (missing tools, missing test setup).
- **impossible**: environment cannot support validation.

**Completion criterion:** validation result is classified and all executed check results are recorded.

## Handoff & Cleanup

Report the worktree path, branch, base commit, diff summary, and validation result. Do not merge, push, rebase, or remove the worktree without an explicit user request. Commit validated batches on the dedicated branch only when the user asked for commits; in-place runs follow the same rule for the primary branch. After the user merges or abandons the branch, remove the worktree with `git worktree remove <path>` and prune stale metadata with `git worktree prune`; leave a dirty worktree in place until the user explicitly requests removal, and preserve its branch until the user decides.

## State & Resumption

When `state_persist` is available, persist audit state to `.code-health-state.json` at the primary repo root after each phase (schema and field meanings in `templates/code-health-state.json`): configuration, capability map, project map, modules analyzed/pending, findings with status, isolation (worktree path, branch, base, status), answers (plan confirmation, fix selection method and detail, risky confirmation, blocker decision), fixes applied, validation results, sources consulted, limitations. The state file is audit metadata, not a fix: keep it out of commits and out of the isolation cleanliness check. This enables resuming an interrupted run without re-analyzing completed modules.

On resume, re-verify that the recorded worktree exists and is on the recorded branch before editing, unless `isolation.status` is `merged`, `removed`, or `abandoned`. If it is missing, recreate it at the recorded path on the recorded branch from the recorded base commit; if recreation fails, ask `fix_blocked` with the reason. Reuse recorded answers in `config`, `isolation`, and `answers`; ask only questions whose answers are missing or invalidated by changed inputs.

When `state_persist` is unavailable: keep findings in context and track progress via `task_manage`. Resumption is limited.

## Context Management for Large Repos

- Process modules in batches; write intermediate findings to state after each batch; drop raw code from context once a module summary exists.
- Prioritize: entry points, auth, data access, config > utility files, tests, docs.
- Re-read a file before applying a fix (it may have changed). Invalidate a module's findings if its files changed after analysis.
- Use subagents to parallelize and keep each agent's context focused.

## Restrictions

- Do NOT apply any change without explicit user authorization. `audit-auto` is the only exception: it auto-fixes only confidence=confirmed AND `fix_risk=low` (SAFE) findings.
- Do NOT call the ask mechanism with a bare prompt, an empty parameter set, or options outside the catalog entry (including its project-map data source). One question carries one decision.
- Do NOT edit source files in the primary worktree, switch its branch, or commit to it during a fix run, except under an explicit `isolation=in-place` or `fix_blocked=in_place` approval. Fixes otherwise go only in the isolated worktree; merge, push, rebase, and removal require explicit authorization.
- Do NOT stash, reset, or commit the user's existing changes to obtain a clean base. Ask `fix_blocked` from the catalog instead.
- Do NOT validate against the primary worktree while a worktree is active.
- Do NOT modify production code beyond the minimal safe fix for a confirmed finding.
- Do NOT claim validation passed if it was not executed.
- Do NOT assume tools, commands, or frameworks exist before inspecting the project.
- Do NOT load the entire codebase into context for repos >50 files.
- Do NOT skip the version-specific research phase. A fix valid for one version may break another.
