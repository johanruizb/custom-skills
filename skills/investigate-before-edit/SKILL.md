---
name: investigate-before-edit
description: "Use before any code modification. Forces an investigation phase that inspects the codebase with harness tools before editing, so decisions are backed by evidence rather than assumptions. Presents a research summary and asks for confirmation on destructive or ambiguous changes."
license: MIT
metadata:
  author: Hermes Agent
  version: "1.1.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [investigation, pre-edit, root-cause, codebase-analysis, evidence-driven, harness-agnostic]
    related_skills: [codebase-audit]
---

# Investigate Before Edit

## Overview

Every code change carries risk. Assumptions about technologies, patterns, APIs, or data flow produce patches that fix symptoms, duplicate existing utilities, or break unrelated callers. This skill enforces a mandatory investigation phase before any file is created, edited, moved, or deleted — the agent must inspect the codebase with the tools available in its harness and ground every decision in evidence it observed, not in guesses.

**Iron law:**

```
Edit only after the investigation summary is presented.
```

Complete the Investigation Phase before proposing or applying any change. This applies to bug fixes, feature work, refactors, config changes, and migrations alike.

## When to Use

- Before any task that will create, edit, move, or delete a source file, config file, or migration.
- When the user asks to fix, add, change, remove, or refactor something in the codebase.
- Before proposing a solution to a bug or unexpected behavior.

Don't use for:
- Pure research or explanation tasks with no planned modification (investigation is the deliverable, no edit gate is needed).
- Trivial typo fixes in a single file you have already read in this session — but re-read if the file may have changed.

## Harness Adaptation

This skill is written in terms of *capabilities*, not tool names. Before starting, discover which tools are available in the current environment and map them:

| Capability | Typical Hermes tool | Fallback |
|---|---|---|
| Read file contents | `read_file` | `terminal` cat |
| Search file contents | `search_files` (target=content) | `terminal` grep/rg |
| Find files by name | `search_files` (target=files) | `terminal` find/ls |
| Execute shell commands | `terminal` | — |
| Edit files | `patch` / `write_file` | `terminal` sed |
| Ask user | `clarify` | conversational reply |
| Delegate investigation | `delegate_task` | sequential self-investigation |
| Web research | `web_search` / `web_extract` | — |
| Task tracking | `todo` | notes in context |

Do NOT assume a tool exists. If a capability is missing, note it as a limitation and adapt the investigation depth accordingly. Never substitute a guess for a tool you don't have — tell the user what you couldn't verify.

## Investigation Phase (mandatory, before any edit)

Complete every step. Each step has a completion criterion. Do not skip steps because the task "looks simple" — simple tasks have root causes and hidden dependencies too.

### 1. Map the project structure

Identify the repository root, top-level directories, and how the codebase is organized. Read any AGENTS.md, CLAUDE.md, .cursorrules, README, or contributing guide present — these encode project conventions that override your defaults.

**Actions:** search for files by name to find manifests and config; read AGENTS.md / README.

**Completion criterion:** the top-level tree and the located subsystem are written into the summary.

### 2. Detect technologies and versions

Read the project manifests (package.json, pyproject.toml, requirements.txt, go.mod, Cargo.toml, etc.) and lockfiles. Record exact framework and library versions. Do NOT assume a stack from file extensions alone.

**Completion criterion:** the languages, frameworks, key libraries, and their versions are recorded. Any version that affects the solution approach is flagged.

### 3. Read configuration files

Inspect settings, env examples, docker-compose, CI configs, lint configs, and build configs that relate to the task. Note test commands, lint commands, and build commands — you will need them for validation.

**Completion criterion:** the config files relevant to the task have been read; the available validation commands (test, lint, build, typecheck) are known.

### 4. Locate entry points and the affected area

Find the application entry points and trace from there to the module(s) the task touches. Identify the specific files, components, services, or endpoints involved.

**Completion criterion:** the set of files directly related to the task is enumerated — not guessed from names, but confirmed by reading or searching.

### 5. Follow the data and execution flow

Trace how data reaches the affected code and where it goes afterward. For a backend change: request → view → serializer → model → signal → response. For a frontend change: component → hook → API → reducer → render. Read each hop; do not assume the shape of an intermediate function.

**Completion criterion:** the full path from input to output through the affected code is understood and can be narrated with file:line references.

### 6. Search for existing implementations and utilities

Before proposing anything new, search the codebase for existing abstractions, helpers, utils, mixins, or services that already do what you need. Check for similar patterns in sibling modules. The project may already have the tool you're about to build.

**Actions:** search file contents for function names, class names, and behavioral keywords related to the task.

**Completion criterion:** a list of existing reusable abstractions exists. If a suitable one is found, the proposal reuses it instead of creating a parallel implementation.

### 7. Identify conventions and architectural patterns

Note the project's naming conventions, layering rules, error-handling style, test structure, and any documented anti-patterns (AGENTS.md usually lists these). The solution must follow existing patterns, not import foreign ones.

**Completion criterion:** the conventions the change must follow are known, including any explicit anti-patterns to avoid.

### 8. Find related tests and validation commands

Locate the tests that cover the affected area. Identify the exact command to run them (pytest path, npm test, cargo test, etc.). If no test covers the area, note that a new test may be needed.

**Completion criterion:** the test command for the affected area is known and has been confirmed to exist (or the gap is recorded).

### 9. Determine root cause (for bug-fix tasks)

When the task is a bug fix, do not stop at the first suspicious line. Trace the symptom to its origin. Check sibling call paths for the same flaw. A symptom fix that leaves the root cause in place will recur.

For any non-trivial bug, work systematically: build a tight feedback loop, form ranked hypotheses, and test each one minimally before touching code.

**Completion criterion:** the root cause is stated with evidence (file:line + code snippet), not a guess. Sibling paths with the same flaw are checked.

### 10. Assess blast radius

Search for all references to the symbols, files, endpoints, or components you plan to touch. List every caller, importer, and dependent. Changes that look local often ripple through importers, tests, serializers, and frontend hooks.

**Actions:** search file contents for the symbol/file name across the whole repo (not just the current directory).

**Completion criterion:** every reference site is enumerated. The change is scoped to the minimum that fixes the root cause without collateral damage.

## Investigation Summary (gate before editing)

Before modifying anything, present a brief summary to the user. Differentiate clearly between **observed facts** (with file:line evidence), **conclusions** you drew, and **assumptions** you could not verify.

The summary must include:

1. **Current implementation** — how the affected area works today, with file references.
2. **Files and components involved** — the enumerated set from steps 4–5 and 10.
3. **Root cause** (for bugs) or **gap** (for features) — stated with evidence.
4. **Proposed solution** — what you will change and why, referencing existing patterns/utilities it reuses.
5. **Affected parts of the system** — the blast radius from step 10.
6. **Validation plan** — which tests, linters, type checks, or builds you will run, and any new tests you will add.

After the summary:

- If the change is **destructive, ambiguous, or has multiple valid strategies**, ask the user for confirmation before proceeding.
- If the change is **small, well-scoped, and clearly what the user asked for**, you may proceed directly to implementation — but still present the summary first so the user can course-correct.

## Implementation Phase (after investigation is complete)

Once the summary is acknowledged:

1. **Follow existing patterns.** Match the project's style, layering, and conventions recorded in step 7. Do not introduce foreign patterns without justification.
2. **Fix the root cause.** Attack the origin identified in step 9, not the symptom. For features, fill the gap with the minimal abstraction that fits the architecture.
3. **Keep the diff minimal.** Touch only what the task needs. No drive-by refactors, renames, or reformatting. Any import or dependency your code requires must be added explicitly.
4. **Add or update tests.** If the area had no coverage, add a regression test. If it had coverage, ensure it still passes and add cases for the new behavior.
5. **Verify between independent tasks when implementing a batch.** When the plan contains multiple independent tasks (e.g., 5 separate fixes from one issue), run lint + build (or the fastest available validation) after each task, not just at the end. This isolates regressions to the task that introduced them. Only run the full test suite once at the end — the intermediate checks are fast gates (lint + build) that catch syntax errors, import breaks, and obvious regressions before they compound.
6. **Run full validations.** Execute the test, lint, typecheck, and build commands discovered in step 3. Record which ran, which passed, and which could not run.
7. **Review the final diff.** Inspect the generated diff for accidental changes, stray imports, or debug logs. Use `git diff` before declaring done.
8. **Report.** Inform the user what was modified, why, and how it was verified. Separate observed facts from conclusions from assumptions in the final report.

## Restrictions

- **No modifications during the investigation phase.** Read and search only. The first file edit or file-creating shell command must come after the summary.
- **Review the directly related files before proposing a solution.** Naming a file is not enough; read it.
- **Reuse an existing abstraction; when none fits, justify the new one in writing.**
- **Follow the project's pattern over your default.** Replace an existing solution with a generic alternative only with written justification.
- **When step 9 shows the root cause is architectural, say so and discuss with the user** instead of papering over it with a quick patch.
- **State only requirements, APIs, models, routes, components, fields, and behaviors you have seen in the repo or a manifest.** If you haven't seen it, go look. Check the manifest and neighboring imports before assuming a library is available.
- **Review all relevant sites when searching for references and dependencies,** not just the first hit.

## Execution Discipline: Finish the Active Plan Before Moving On

When a plan is in progress (tracked in a task list or a plan file), do NOT suggest new work, declare the task done, or pivot to a different topic until every item in the plan is complete. Finish the plan first. Only after the last task is verified and committed should you ask "what's next."

This applies even when:
- A subagent reports completion but you haven't verified it yet
- A task seems "good enough" or "close enough"
- The user asks a tangential question that could be answered briefly
- You think of a useful improvement or refactor

Answer the tangential question concisely, then return to the plan. Do not let side conversations derail the active plan.

## When to Pause and Ask

Ask the user when:

- The investigation reveals multiple valid strategies with meaningful tradeoffs.
- The change is destructive (deleting files, dropping columns, breaking APIs).
- The root cause is ambiguous and two hypotheses both fit the evidence.
- A required capability (tool, test setup, database) is missing and blocks validation.
- The task as described conflicts with a project convention or anti-pattern found in step 7.

Do not ask for confirmation on small, well-scoped changes that clearly match the user's request — present the summary and proceed.

## Parallel Investigation with Subagents

When the task spans multiple independent areas (e.g., backend + frontend, or several unrelated modules), and subagent delegation is available, dispatch subagents to investigate each area in parallel. Each subagent must follow the same Investigation Phase steps and return its findings as structured evidence (file:line references, not prose).

Main agent responsibilities when using subagents:

- Consolidate findings, resolve contradictions, and verify evidence by re-reading the cited locations.
- Subagent summaries are self-reports, not verified facts. For operations with external side-effects, verify the handle (URL, file path, ID) yourself.
- Never let a subagent apply edits during the investigation phase — investigation only.

## Project-Specific References

Case-study references extracted from real investigations. Consult the one matching the task area before or during the Investigation Phase:

- `references/django-drf-multitenant-permissions.md` — middleware ordering, DRF authentication timing, and custom permission classes (complements pitfall 15).
- `references/django-env-var-cleanup.md` — investigation pattern for cleaning up `.env.example`, dead environment variables, and Docker Compose/settings config.
- `references/iglesiaapp-ui-patterns.md` — established frontend UI layout and MUI component patterns to follow when the change touches UI in that style of project.
- `references/mui-listitembutton-nested-link.md` — full pattern for the nested `<a>` ListItemButton bug (pitfall 26).
- `references/spanish-english-permission-names.md` — inventory of affected files for the permission-key mismatch (pitfall 27).

## Common Pitfalls

1. **Skipping the investigation because the fix "looks obvious."** Obvious fixes mask root causes. Run the phase anyway; it's fast for simple tasks and prevents rework.

2. **Reading file names but not file contents.** A file called `utils.py` doesn't tell you what's in it. Read the relevant files; search for the symbols you plan to touch.

5. **Inventing an API or import you didn't verify.** If you haven't seen the function, class, or export in the repo or a manifest, it doesn't exist for your purposes. Go look.

7. **Replacing a project pattern with a generic best practice.** The project's conventions win. A "better" pattern that diverges from the codebase creates inconsistency and review friction.

8. **Skipping validation because tests are slow.** Run the relevant subset at minimum. State exactly what ran and what didn't. Never claim validation passed if it was not executed.

9. **Bundling refactors into a fix.** "While I'm here" changes expand the blast radius and make review harder. Keep the diff minimal; log refactor ideas separately.

10. **Not differentiating facts from assumptions in the report.** The user needs to know which parts of your conclusion are evidence-backed and which are inferences. Label them.

11. **Not verifying that patches persist after application.** When working in a repo with uncommitted changes from prior sessions, patches can be silently reverted by `git checkout`, `git stash`, or a merge. After applying any patch, re-read the file to confirm the change is present. Before starting a new session, verify that previous patches are still in place.

Project-specific pitfalls: see `references/project-pitfalls.md`.

## Verification Checklist

Before declaring the task complete:

- [ ] Investigation Phase: all 10 steps completed with recorded evidence
- [ ] Investigation Summary presented to the user (current impl, files, root cause, proposal, blast radius, validation plan)
- [ ] Confirmation obtained for destructive or ambiguous changes
- [ ] Edits follow existing project patterns and conventions
- [ ] Root cause addressed, not just the symptom
- [ ] Diff is minimal — no drive-by refactors or unrelated changes
- [ ] Existing reusable abstractions reused; no parallel implementation created
- [ ] Tests added or updated for the changed behavior
- [ ] Available validations run: test / lint / typecheck / build — results recorded
- [ ] Final diff reviewed via `git diff` — no accidental changes
- [ ] Final report separates observed facts from conclusions from assumptions

User memory test-run preferences override the validation defaults.