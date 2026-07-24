---
name: simplify-codebase
description: "Analyze an entire codebase for accidental complexity — duplication, unnecessary abstractions, redundant dependencies, dead code, inconsistent patterns — then propose and apply a prioritized simplification plan. Harness-agnostic: discovers available tools at runtime and adapts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [simplification, deduplication, complexity, refactoring, codebase-analysis, harness-agnostic]
    related_skills: [improve-codebase-architecture, codebase-audit, investigate-before-edit, simplify-code, codebase-design]
---

# Simplify Codebase

Analyze an entire codebase to find and reduce accidental complexity — the kind that accumulates when working continuously with AI tools: duplicated logic, unnecessary abstractions, utilities that wrap single calls, dead code, inconsistent patterns, and redundant dependencies. The goal is a simpler, more maintainable codebase without altering existing behavior or introducing regressions.

**Core motivation:** AI-assisted development can introduce layers, wrappers, duplicated utilities, and parallel implementations without considering the whole system. This skill systematically counteracts that tendency.

## When to Use

- User asks to "simplify the codebase", "reduce complexity", "deduplicate code", "clean up the whole project", or "find and remove dead code".
- User wants a comprehensive map of the codebase's modules, dependencies, responsibilities, and complexity hotspots.
- User suspects AI-generated code has accumulated accidental complexity.
- User wants a prioritized simplification plan before making changes.

Don't use for:
- Cleaning up only recent git changes (use `simplify-code` instead).
- Finding bugs, security issues, or performance problems (use `codebase-audit` instead).
- Deepening shallow modules into deep ones (use `improve-codebase-architecture` instead).
- Investigating before a single edit (use `investigate-before-edit` instead).

## Harness Adaptation

This skill is written in terms of *capabilities*, not tool names. Before starting, discover which tools are available and map them:

| Capability | Typical Hermes tool | Fallback |
|---|---|---|
| Read file contents | `read_file` | `terminal` cat |
| Search file contents | `search_files` (target=content) | `terminal` grep/rg |
| Find files by name | `search_files` (target=files) | `terminal` find/ls |
| Execute shell commands | `terminal` | — |
| Edit files | `patch` / `write_file` | `terminal` sed |
| Ask user | `clarify` | conversational reply |
| Delegate analysis | `delegate_task` | sequential self-analysis |
| Web research | `web_search` / `web_extract` | — |
| Task tracking | `todo` | notes in context |
| Vision / screenshots | `browser_vision` | — |

Do NOT assume any tool exists. If a capability is missing, note it as a limitation and adapt accordingly.

## Phase 1: Project Discovery

Map the codebase before touching anything.

1. **Find the repository root** (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.).
2. **Map directory structure** using `search_files(target='files')` and `terminal` (ls/find). Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, `migrations` (unless looking for migration-specific patterns).
3. **Identify technologies and versions**: read manifests and lockfiles. Record exact framework/library versions. Do NOT assume a stack from file extensions.
4. **Read project conventions**: AGENTS.md, CLAUDE.md, .cursorrules, README, contributing guides, lint configs, pre-commit configs. These encode rules the simplification must respect.
5. **Identify entry points, test directories, config directories, and documentation**.
6. **Record validation commands**: test runner, linter, type checker, build command. You will need these after every change.
7. **Divide the codebase into analyzable modules** based on directory structure and logical boundaries.

**Completion criterion**: a structured project map exists with technologies, versions, module list, entry points, test setup, validation commands, and exclusion list.

## Phase 2: Deep Analysis

Analyze the codebase module by module. Use `delegate_task` to dispatch subagents per module/area when available — they run in parallel and return structured findings. The main agent consolidates.

**Critical rule: VERIFY everything in the code.** Do not assume how something works based on naming, conventions, or training data. Read the actual files. Search for actual references. Trace actual call paths.

For each module, look for the categories described in `references/analysis-checklists.md`:

### 2.1 Code Duplication
- Functions/methods that duplicate existing functionality (same logic, different names).
- Copy-paste blocks with minor variations that could share a single implementation.
- Similar utility functions scattered across modules.
- Re-implemented standard library / framework functionality.
- Parallel implementations of the same concept (e.g., two validators, two formatters, two API callers for the same service).

### 2.2 Unnecessary Abstractions
- Wrappers that add no value (single-call wrappers, pass-through layers).
- Interfaces/abstract classes with a single implementation and no planned variation.
- Factory classes that always return the same type.
- Builder patterns where a simple constructor would do.
- Manager classes that just delegate to another class.
- Generic helpers so abstract they're harder to use than the direct code.

### 2.3 Redundant Responsibilities
- Multiple modules/components doing the same job.
- Overlapping utility files (utils.py, helpers.py, common.py with overlapping content).
- Duplicate configuration logic across modules.
- Multiple error-handling patterns doing the same thing differently.

### 2.4 Redundant Dependencies
- Dependencies declared but never imported/used.
- Multiple libraries doing the same job (e.g., both `requests` and `httpx` when one suffices — but only flag if the project actually uses both for the same purpose; a migration in progress is a valid reason).
- Internal modules that wrap a single external call and add no value.

### 2.5 Excessively Complex Flows
- Call chains so long they could be flattened (A→B→C→D where B and C are pass-throughs).
- Conditional logic with deeply nested branches that could be simplified.
- State machines that could be replaced with simple conditionals.
- Configuration loading that goes through 5 layers when 2 would do.

### 2.6 Dead or Apparently Unused Code
- Functions, classes, methods, constants never referenced.
- Commented-out code blocks.
- Unused imports.
- Unused variables.
- Files not imported by anything.
- Disabled features behind flags that are never enabled.

**CRITICAL**: Before flagging anything as dead/unused, search for ALL reference types:
- Direct imports (`from x import y`, `import x.y`)
- Dynamic references (`getattr(module, 'name')`, `importlib`)
- String-based references (settings, configs, serializers.Meta, Django URL patterns)
- Template references (Django templates, Jinja2, React components referenced by string)
- Signal handlers, decorators, middleware registered by string path
- Management commands referenced by name
- Test files that import the code
- Configuration files that reference the code (settings.py, urls.py, INSTALLED_APPS, etc.)
- Migration files that reference models

If ANY reference is found, do NOT flag as dead. If uncertain, mark as `confidence: low` with a note explaining what was checked.

### 2.7 Inconsistent Patterns
- Same operation done differently across modules (e.g., some modules use a custom API wrapper, others use raw `fetch`/`requests`).
- Inconsistent error handling (try/except in some, .catch() in others, no handling elsewhere).
- Inconsistent naming conventions for the same concept.
- Inconsistent file organization patterns (some modules have `views.py` + `serializers.py`, others have everything in `models.py`).
- Inconsistent test patterns (some use factories, some manual setup, some fixtures).

**Completion criterion**: every module has been analyzed; raw findings are recorded with file:line evidence. See `references/finding-format.md` for the structured format.

## Phase 3: Build the Codebase Map

Consolidate all findings into a structured map. This is the deliverable that explains the codebase.

### 3.1 Structure Overview
- Directory tree (top 3 levels, excluding noise).
- Technology stack summary.
- Entry points and bootstrap flow.

### 3.2 Module Inventory
For each module:
- **Name and path**
- **Responsibility**: what it does (1-2 sentences).
- **Dependencies**: what it imports/depends on (internal and external).
- **Dependents**: what depends on it (who imports it).
- **Complexity assessment**: low / medium / high (with reasoning).
- **Test coverage**: has tests / no tests / partial tests.
- **Technical debt indicators**: any findings from Phase 2 that apply.

### 3.3 Dependency Graph
- Internal module-to-module dependencies.
- External library dependencies (key ones).
- Circular dependencies (if any found).
- Layers/tiers (if the project has layered architecture).

### 3.4 Complexity Hotspots
- Modules/files with the highest finding count.
- Areas with the most duplication.
- Areas with the deepest call chains.
- Areas with the most inconsistent patterns.

**Completion criterion**: a complete codebase map document exists. Present it to the user before proceeding to the simplification plan.

## Phase 4: Simplification Plan

Produce a prioritized plan based on the findings. Each proposed change must be classified:

### Classification

**Risk level:**
- **SAFE**: Proven not to affect behavior (unused imports, dead code with zero references, commented-out blocks, exact duplicates where one copy is never called).
- **CAREFUL**: Improves without changing semantics (consolidating duplicates, removing pass-through wrappers, simplifying conditionals, renaming for consistency). Requires test verification.
- **RISKY**: May change behavior or breaks contracts (removing "unused" code with uncertain references, changing public APIs, restructuring module boundaries, removing dependencies). Requires explicit user confirmation.

**Impact level:**
- **HIGH**: Reduces complexity across multiple files/modules, removes significant duplication, or simplifies a core flow.
- **MEDIUM**: Improves one module or removes moderate duplication.
- **LOW**: Minor cleanup (unused imports, commented code removal).

**Priority ordering (highest first):**
1. SAFE + HIGH impact
2. SAFE + MEDIUM impact
3. CAREFUL + HIGH impact
4. CAREFUL + MEDIUM impact
5. SAFE + LOW impact
6. CAREFUL + LOW impact
7. RISKY + any impact (requires explicit confirmation, done last)

### Plan Format

See `templates/simplification-plan.md` for the template. Each item in the plan must include:

- ID (SIMPL-001, SIMPL-002, ...)
- Title
- Category (duplication, abstraction, dead-code, inconsistency, complexity, dependency)
- Files affected
- Description of the problem (with evidence: file:line)
- Proposed change
- Risk: SAFE / CAREFUL / RISKY
- Impact: HIGH / MEDIUM / LOW
- Dependencies on other items (do X before Y)
- Validation: which tests/linters to run after this change
- Estimated effort: trivial / small / medium / large

### Restrictions on the Plan

- Do NOT propose new abstractions unless they clearly reduce complexity. A new abstraction that's harder to maintain than the duplication it replaces is a net loss.
- Do NOT propose replacing simple duplication with a complex architecture. If two similar functions differ in one line, a shared function with a parameter is fine; a strategy pattern is not.
- Do NOT propose mass refactors. Group changes into small, independently verifiable batches.
- Do NOT propose changes to code you haven't read and verified.
- Do NOT propose removing code without verifying all reference types (see Phase 2.6).

**Completion criterion**: a prioritized, classified plan exists. Present it to the user and ask for confirmation before applying any changes. Use `clarify` if available, or ask conversationally.

## Phase 5: Apply Changes

After user confirmation, apply changes in priority order. For each change:

1. **Re-read the affected files** (they may have changed since analysis).
2. **Apply the minimal change** using `patch` or `write_file`.
3. **Search for references** to any renamed/removed symbols to ensure all call sites are updated.
4. **Run validation** after each change group (not just at the end):
   - Fastest available check first (lint, typecheck, build).
   - Then the test suite (or the relevant test subset for the touched area).
   - If a change breaks tests, **revert that specific change** and report it. Do not continue piling changes on top of a broken state.
5. **Record the diff** for each applied change.
6. **Update the plan status** (pending → in-progress → done / skipped / reverted).

### Execution Discipline

- **Progressive application**: Apply changes in small batches (1-5 related changes at a time). Run validation after each batch. Do not apply 50 changes at once.
- **One file at a time for CAREFUL changes**: Apply the change, verify, move to the next.
- **Explicit confirmation for RISKY changes**: Present each RISKY change individually with its risk description and ask the user before applying. Do not batch RISKY changes.
- **If a change introduces a regression**: Revert it immediately. Record the failure. Move to the next independent change. Do not try to fix the regression while other changes are pending.
- **Subagent collateral damage check**: If using `delegate_task` subagents to apply changes, always run `git diff --stat HEAD` and `git status --short` after all subagents complete. Revert any unintended modifications.

**Completion criterion**: all approved changes have been applied (or skipped with documented reasons), and validation has been run after each batch.

## Phase 6: Test & Validate

After all approved changes are applied:

1. **Run the full test suite** (not just the subset).
2. **Run linters** (the project's linter config).
3. **Run type checkers** (mypy, tsc, pyright, etc.).
4. **Run build/compile**.
5. **Run any project-specific validators** (Django: `manage.py check`, React: `npm run build`, etc.).
6. **Review the final diff** with `git diff --stat` and `git diff` to ensure no accidental changes.

If tests fail:
- Identify which change caused the failure (use `git stash` / `git diff` to bisect if needed).
- Revert the offending change.
- Re-run tests to confirm they pass again.
- Report the reverted change in the final summary.

**NEVER claim validation passed if it was not executed.** State exactly what ran, what passed, what failed, and what couldn't run.

**Completion criterion**: validation has been run and results are recorded. Any regressions have been reverted.

## Phase 7: Final Report

Deliver a summary using the template in `templates/final-report.md`. The report must include:

### 7.1 Codebase Map Summary
- Structure overview (condensed from Phase 3).
- Module count, total files, languages.
- Complexity hotspot summary.

### 7.2 Changes Applied
For each applied change:
- ID, title, category
- Files affected (with paths)
- What was changed (1-2 sentences)
- Risk level that was assigned
- Validation result (passed / failed / reverted)

### 7.3 Metrics
- Duplications eliminated (count)
- Dead code removed (lines / files)
- Abstractions removed (count)
- Complexity reduced (qualitative: which flows are now simpler)
- Files affected (total count)
- Net line change (added / removed)

### 7.4 Risks Detected
- Any RISKY changes that were proposed but not applied (and why).
- Any regressions found during validation (and whether they were reverted).
- Any areas where simplification was possible but deemed too risky without more context.

### 7.5 Validations Executed
- Test suite: command, result, pass/fail counts.
- Linter: command, result.
- Type checker: command, result.
- Build: command, result.
- Any that could not run (with reason).

### 7.6 Opportunities Pending
- Findings not addressed (lower priority, RISKY without confirmation, or requiring more context).
- Recommended next steps.
- Areas that would benefit from deeper analysis (e.g., with `improve-codebase-architecture` or `codebase-audit`).

**Completion criterion**: the user has received the full report.

## Subagent Strategy

When `delegate_task` is available, use it to parallelize Phase 2 (analysis). Split work by module/area:

| Subagent | Task | Input | Output |
|---|---|---|---|
| Module analyst (per module) | Full analysis of a module subset | Module path + analysis checklists + finding format | Structured findings |
| Duplication detector | Cross-module duplication search | All module paths + finding format | Duplication findings |
| Dead code hunter | Dead code search with reference verification | All source paths + finding format | Dead code findings |
| Consolidator | Deduplicate, verify, rank all findings | All subagent outputs | Consolidated finding list |

Each subagent must:
- Receive: project map, module list, analysis checklists, finding format.
- Return structured findings only (no edits, no plans).
- Search the codebase for evidence — don't guess. Every finding must cite file:line.
- Verify references before flagging dead code (all reference types, not just imports).

The main agent:
- Consolidates all findings, deduplicates, resolves contradictions.
- Verifies evidence by re-reading cited locations.
- Builds the codebase map and simplification plan.

**Pitfall**: Subagents can modify files as collateral damage. After all subagents return, run `git diff --stat HEAD` and `git status --short`. Revert any unintended changes with `git checkout -- <path>`.

## Common Pitfalls

1. **Assuming how code works without reading it.** Naming is not behavior. A function called `validate_user` might not validate anything. Read the actual implementation before proposing changes.

2. **Flagging code as dead without checking all reference types.** Django URL patterns, signal handlers, settings references, dynamic imports, template references, and management command registrations are easy to miss. Always search comprehensively. When in doubt, mark as `confidence: low` and let the user decide.

3. **Proposing abstractions that are more complex than the duplication.** Two similar 10-line functions are often better than one 15-line function with 3 parameters. Apply the deletion test: would removing the proposed abstraction concentrate complexity, or just add a layer?

4. **Mass refactoring in one shot.** Apply changes progressively, validate after each batch. If you apply 50 changes at once and tests break, you can't tell which change caused it.

5. **Not respecting project conventions.** If the project has a consistent pattern that you find "ugly" but works and is tested, do NOT propose changing it just for style. Only flag patterns that are genuinely inconsistent *within the project* or causing real complexity.

6. **Removing "unused" code that's actually used dynamically.** Django uses string references extensively (settings, URL patterns, serializers.Meta.model, signal string paths). Always grep for the string name, not just the import statement.

7. **Treating AI-generated code as inherently bad.** The goal is to reduce complexity, not to remove code because an AI wrote it. Evaluate each piece on its merits: does it add value? Is it duplicated? Is it dead? If it's clean, tested, and useful, leave it.

8. **Skipping validation because "the change is trivial."** Even removing an unused import can break things if it's re-exported elsewhere. Run the fast checks (lint, build) after every batch.

9. **Not differentiating facts from assumptions.** In the report, clearly separate what you verified (file:line evidence) from what you inferred. The user needs to know which findings are solid and which are uncertain.

10. **Proposing to replace duplication with a more complex abstraction.** The restriction is clear: "No reemplazar duplicación simple por arquitecturas más difíciles de mantener." If the deduplication requires a new class hierarchy, factory, or generic framework, it's probably not worth it. A shared function or a constant is fine; a plugin system is not.

## Verification Checklist

- [ ] Phase 1: Project map complete (technologies, versions, modules, entry points, validation commands)
- [ ] Phase 2: Every module analyzed; findings recorded with file:line evidence
- [ ] Phase 2: Dead code findings verified against all reference types
- [ ] Phase 3: Codebase map built and presented to user
- [ ] Phase 4: Simplification plan prioritized, classified (SAFE/CAREFUL/RISKY), presented
- [ ] Phase 4: User confirmed which changes to apply
- [ ] Phase 5: Changes applied in priority order, progressively, with validation after each batch
- [ ] Phase 5: Any regression was reverted and recorded
- [ ] Phase 6: Full validation run (test, lint, typecheck, build) — results recorded
- [ ] Phase 7: Final report delivered with all sections complete
- [ ] Report separates verified facts from assumptions
- [ ] Opportunities pending are listed with recommendations