---
name: codebase-audit
description: "Use when the user wants a deep audit of an entire codebase for performance, bugs, and/or security issues. Discovers available tools at runtime, adapts to any harness (Hermes, Claude Code, OpenCode, etc.), reviews all source code (not just diffs), and optionally fixes selected findings."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [audit, performance, bugs, security, codebase, review, harness-agnostic]
    related_skills: [requesting-code-review, systematic-debugging, improve-codebase-architecture, test-suite-improver]
---

# Codebase Audit

Deep audit of an entire codebase for performance, bugs, and/or security. Reviews all source code — not just diffs or recent changes. Harness-agnostic: discovers available tools at runtime and adapts. Optionally fixes selected findings with validation.

## When to Use

- User asks to audit, review, or find issues in a codebase (performance, bugs, security, or all).
- User wants a comprehensive codebase health check before a release, migration, or refactoring.
- User wants to find and optionally fix security vulnerabilities across the whole project.
- User wants a performance review of the entire codebase, not just changed files.

Don't use for:
- Reviewing only recent git changes (use `requesting-code-review` instead).
- Debugging a specific known bug (use `systematic-debugging` instead).
- Architecture-level refactoring decisions (use `improve-codebase-architecture` instead).

## Architecture: Core + Adapters

This skill separates harness-independent logic from harness-specific tool binding.

**Core logic** (this file): project discovery, audit planning, analysis methodology, finding format, consolidation, fix application, validation, reporting. Written entirely in terms of *capabilities* — never names specific tools.

**Harness adapter** (loaded from `references/harness-adapters.md`): maps capabilities to concrete tools available in the current environment. Selected at runtime based on detected harness.

Capabilities the core depends on (adapter must provide or flag as missing):

| Capability | Purpose |
|---|---|
| `file_read` | Read file contents |
| `file_search` | Search file contents (regex/grep) |
| `file_find` | Find files by name/glob |
| `file_write` | Edit/create files |
| `dir_list` | List directory contents |
| `cmd_exec` | Execute shell commands |
| `git_query` | Query git (log, diff, branches) |
| `web_search` | Search the web |
| `web_extract` | Extract web page content |
| `user_ask` | Ask user structured questions (multiple choice, confirmation) |
| `subagent_spawn` | Delegate tasks to subagents |
| `task_manage` | Manage a todo/task list |
| `state_persist` | Persist state across interruptions |
| `html_open` | Open an HTML file in a browser |

See `references/harness-adapters.md` for per-harness bindings and the fallback generic adapter.

## Phase 1: Tool Discovery & Adapter Selection

1. Detect which tools are available in the current environment. Do NOT assume any tool exists.
2. For each capability in the table above, determine: available (which tool), or missing.
3. Select the matching harness adapter from `references/harness-adapters.md`. If no specific match, use the generic adapter.
4. Record the capability map. Missing capabilities are logged as limitations that affect the audit.
5. **Completion criterion**: every capability is classified as available (with concrete tool name) or missing (with impact noted).

## Phase 2: Project Discovery

1. Find the repository root (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `requirements.txt`, `composer.json`, etc.).
2. Map the directory structure using `file_find` and `dir_list`. Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, and any user-specified exclusions.
3. Identify languages, frameworks, build tools, test runners, and infrastructure from config files and dependency manifests.
4. Extract exact versions: language runtime, frameworks, key dependencies. Read lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`, etc.) when present.
5. Identify entry points, test directories, config directories, and documentation.
6. Divide the codebase into analyzable modules/units based on directory structure and logical boundaries.
7. **Completion criterion**: a structured project map exists with technologies, versions, module list, entry points, test setup, and exclusion list.

## Phase 3: Planning & User Configuration

Ask the user — using `user_ask` if available, else conversational — for:

1. **Audit areas**: performance, bugs, security, or all. Default: all.
2. **Scope**: entire repo, specific folders, or specific modules. Default: entire repo.
3. **Exclusions**: additional paths to exclude beyond auto-detected ones.
4. **Depth**: quick (surface patterns), standard (module-by-module deep read), or exhaustive (every file + dependency analysis). Default: standard.
5. **HTML report**: yes/no. Default: no.
6. **Execution mode**:
   - `audit-only` — report findings, no changes.
   - `audit-select` — audit, then user picks fixes interactively.
   - `audit-auto` — audit, then auto-fix all findings classified as safe.
   Default: `audit-select`.
7. **Subagents**: use subagent parallelism if available. Default: yes when available.

Present the plan (scope, modules, order, tools, subagent strategy, exclusions, limitations) to the user for confirmation via `user_ask` or conversationally.

**Completion criterion**: user has confirmed areas, scope, mode, depth, and the plan is recorded.

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

Use the analysis checklists from `references/analysis-checklists.md` for each selected area. For Django/DRF projects, also consult `references/django-drf-performance-patterns.md` for concrete search queries and common findings, and `references/django-drf-multitenant-findings.md` for multi-tenant-specific patterns (IDOR, tenant isolation, rate limiting, serializer exposure).

Process the codebase module by module (or in batches for large repos):

1. **Per module**: read source files, search for anti-patterns, run available linters/static analyzers via `cmd_exec`, cross-reference with the version-specific risk profile from Phase 4.
2. **Global searches**: use `file_search` to find recurring patterns across the codebase (e.g., `eval(`, `innerHTML`, SQL string concatenation, `console.log` in production, `except:`, `catch(Exception`).
3. **Static analysis**: run any available tools — eslint, pylint, bandit, semgrep, go vet, cargo clippy, npm audit, safety, etc. — via `cmd_exec`. Record results.
4. **Record each finding** in the structured format (see Finding Format below). Every finding must include concrete evidence: file, line, code snippet.
5. **No speculation**: if you cannot point to specific code, do not raise the finding. Mark uncertain items as `hypothesis` with `confidence: low`.
6. **Tracking**: use `task_manage` to track which modules are analyzed vs pending. For large repos, write intermediate results to a state file via `state_persist`.
7. **Subagent strategy** (when `subagent_spawn` is available): see "Subagent Strategy" below.
8. **Completion criterion**: every module in scope has been reviewed, all findings recorded with evidence, task list shows no pending modules.

### Subagent Strategy

When subagents are available, split work by area or module:

| Subagent | Task | Input | Output |
|---|---|---|---|
| Area analyst (per area) | Performance, bugs, or security audit | Project map + version risk profile + checklists | Structured findings |
| Module analyst (per module) | Full audit of a module subset | Module list + project map + checklists | Structured findings |
| Consolidator | Deduplicate, verify, rank findings | All subagent outputs | Consolidated finding list |

Each subagent receives: project map, module list, version risk profile, analysis checklists, finding format. Each returns structured findings only.

The main agent: consolidates, deduplicates, verifies evidence, resolves contradictions.

When subagents are NOT available: simulate the same separation by processing areas/modules sequentially within one agent, using the same input/output formats.

## Phase 6: Consolidation

1. Gather all findings from all agents/analyses.
2. Deduplicate: same issue found in same location = one finding. Cross-reference overlapping findings.
3. Group related findings that share a root cause.
4. Verify evidence: re-read the referenced code to confirm it still matches (files may have changed).
5. Assign for each finding:
   - **Severity**: critical, high, medium, low, info.
   - **Confidence**: confirmed (verified in code), probable (strong evidence), hypothesis (needs validation).
   - **Priority**: P0 (fix now), P1 (fix soon), P2 (fix when convenient), P3 (optional improvement).
6. Classify each as: confirmed problem / probable risk / hypothesis / optional improvement.
7. Determine dependency ordering between findings (e.g., fix A before B because B depends on A).
8. **Completion criterion**: a deduplicated, verified, severity-ranked finding list with no unverified evidence.

## Phase 7: Report

Generate a report containing:

- Executive summary (counts by category/severity, top risks).
- Technologies and exact versions detected.
- Tools used and tools that were unavailable (with impact).
- Scope: files/modules analyzed, files/modules omitted.
- Findings grouped by category, each with full structured format.
- Recommended resolution order.
- Audit limitations (missing tools, unverified hypotheses, areas not covered).

Present the report to the user. If HTML report was requested and `file_write` is available, generate it (see `references/html-report.md` and `scripts/generate-html-report.py`).

**Completion criterion**: user has received the full report (inline or HTML or both).

## Finding Format

Every finding MUST contain all of these fields:

```
ID:          Unique identifier (e.g., PERF-001, BUG-003, SEC-002)
title:       Short descriptive title
category:    performance | bugs | security
severity:    critical | high | medium | low | info
priority:    P0 | P1 | P2 | P3
confidence:  confirmed | probable | hypothesis
status:      open | fixing | fixed | wontfix | skipped
module:      Module/subsystem name
file:        Absolute or repo-relative path
lines:       Line range (e.g., "42-58")
description: What the issue is
evidence:    Exact code snippet showing the problem
reasoning:   Why this is a problem
impact:      What could go wrong if unfixed
reproduction: Steps to reproduce (when applicable)
recommendation: How to fix it
fix_risk:    low | medium | high (risk of applying the fix)
tests_needed: What tests should validate the fix
dependencies: IDs of findings that must be fixed first
source:      Technical reference / doc / CVE (when applicable)
detected_by: Tool or agent that found it
```

See `references/finding-schema.md` for JSON examples.

## Selection of Fixes

After presenting the report, ask the user (via `user_ask` if available) which findings to fix. Offer selection by:

- Individual finding ID.
- Category (all performance, all bugs, all security).
- Severity (all critical, all high).
- Confidence (all confirmed).
- Module (all findings in module X).
- All safe fixes (confidence=confirmed, fix_risk=low).
- Exclude specific IDs.
- Audit-only (no fixes).

Do NOT apply any change before receiving explicit authorization. In `audit-auto` mode, auto-fix only findings where confidence=confirmed AND fix_risk=low.

## Phase 8: Fix Application

For each selected finding:

1. Re-read the current code at the finding location (it may have changed since audit).
2. Analyze impact: what else depends on this code? Search for references.
3. Check `source` references for correct fix approach if version-specific.
4. Plan the minimal, safe change. Do NOT refactor unrelated code.
5. Apply the change using `file_write` / file editing tools.
6. Respect project conventions, style, and architecture detected in Phase 2.
7. Add or update tests when appropriate.
8. Record: what was changed, which finding it resolves, the diff.
9. Review the generated diff.
10. Revert or adjust if the change introduces unexpected side effects.
11. **Completion criterion**: each selected finding has a recorded fix with diff, or a documented reason it was skipped.

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

**Ad-hoc verification scripts:** For Django/DRF projects where the full test suite requires a seeded database (and the seed may be incomplete), write a focused Python script that imports Django settings and runs runtime assertions for each fix. This is faster and more reliable than relying on a potentially broken test setup. Example pattern:

```python
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.test')
import django; django.setup()

# Verify fix: serializer no longer exposes password field
from auth.serializers import user_serializer
fields = set(user_serializer().fields.keys())
assert 'password' not in fields, f"password still exposed: {fields}"
assert fields == {'id', 'username', 'email'}, f"unexpected fields: {fields}"

# Verify fix: IDOR tenant filter added
from grupo_cargo.views import some_view
# ... runtime assertions

print("All ad-hoc checks passed.")
```

Run this script via `python script.py` after applying fixes. If it passes, the fixes are verified at the code level even when the full test suite can't run due to environmental constraints.

Classify validation result as one of:

- **passed**: all checks ran and passed.
- **failed**: one or more checks ran and failed.
- **partial**: some checks passed, some could not run.
- **not_run**: validation could not execute (missing tools, missing test setup).
- **impossible**: environment cannot support validation.

NEVER claim validation passed if it was not executed. Clearly state which checks ran, which passed, which failed, and which were unavailable.

**Completion criterion:** validation result is classified and all executed check results are recorded.

## State & Resumption

When `state_persist` is available, record after each phase:

- Audit configuration (areas, scope, mode, depth).
- Capability map (available/missing tools).
- Project map.
- Modules analyzed / pending.
- Findings (full list with status).
- Sources consulted.
- Fixes applied (with diffs).
- Validation results.
- Errors and limitations.

This enables resuming an interrupted audit without re-analyzing completed modules. See `templates/audit-state.json` for the state file format.

When `state_persist` is unavailable: keep findings in context and summarize progress via `task_manage`. Acknowledge that resumption is limited.

## Context Management for Large Repos

- Process modules in batches, never load the entire codebase at once.
- Write intermediate findings to state file after each module.
- Create module summaries after analysis, then drop the raw code from context.
- Prioritize: entry points, auth, data access, config > utility files, tests, docs.
- Re-read a file before applying a fix (it may have changed).
- Invalidate prior findings for a module if that module's files changed after analysis.
- Use subagents to parallelize and keep each agent's context focused.

## Restrictions

- Do NOT apply any fix without explicit user authorization (except in `audit-auto` mode for confirmed, low-risk findings).
- Do NOT modify production code beyond the minimal safe fix for a confirmed finding.
- Do NOT refactor unrelated code during a fix.
- Do NOT claim validation passed if it was not executed.
- Do NOT raise findings without concrete evidence (file + line + code snippet).
- Do NOT assume tools, commands, or frameworks exist before inspecting the project.
- Do NOT load the entire codebase into context for repos >50 files.
- Do NOT skip the version-specific research phase — a fix valid for one version may break another.

## Common Pitfalls

1. **Assuming tools exist.** Always discover first. A missing `cmd_exec` means no linters run. A missing `web_search` means lower confidence on version-specific findings. Record the limitation, don't hide it.

2. **Auditing only changed files.** This is a full-codebase audit. If the user wants only diffs, point them to `requesting-code-review`.

3. **Speculative findings without evidence.** If you cannot point to specific file + line + code, do not raise the finding. Mark uncertain items as `hypothesis` with `confidence: low`.

4. **Claiming validation passed without running it.** Never. State exactly what ran, what passed, what failed, what couldn't run.

5. **Incompatible recommendations.** A fix valid for React 18 may break React 16. Always cross-reference with the version risk profile from Phase 4.

6. **Destructive changes.** Apply the minimal safe fix. Do not refactor unrelated code during a fix. Do not modify files outside the selected scope.

7. **Skipping re-read before fix.** Files change. Always re-read the exact location before applying a fix. A stale finding pointing at the wrong line is worse than no finding.

8. **Not excluding generated/vendor code.** `node_modules`, `dist`, `vendor`, lockfiles, and generated code should be excluded. Analyzing them wastes context and produces noise.

9. **Loading everything into context.** For repos >50 files, use batching, summaries, and subagents. Never try to hold the entire codebase in one context window.

10. **Not offering selection granularity.** After the report, always offer selection by ID, category, severity, confidence, module, and "safe fixes" — not just "fix all or nothing".

## Verification Checklist

- [ ] Tool discovery completed; capability map recorded with missing tools noted
- [ ] Harness adapter selected and loaded
- [ ] Project map complete: technologies, versions, modules, entry points, tests
- [ ] User confirmed: areas, scope, depth, mode, exclusions, subagent preference
- [ ] Version-specific risk profile built with sources cited
- [ ] Every module in scope audited; task list shows zero pending
- [ ] All findings have: ID, evidence (file+line+snippet), severity, confidence, recommendation
- [ ] Findings deduplicated, cross-referenced, dependency-ordered
- [ ] Report presented to user (inline and/or HTML)
- [ ] Fix selection captured via user interaction
- [ ] Each selected fix applied with minimal diff, re-read before edit
- [ ] Validation run: each check classified as passed/failed/not_run/impossible
- [ ] State file updated (when persistence available)
- [ ] Limitations section in report: missing tools, unverified hypotheses, omitted areas