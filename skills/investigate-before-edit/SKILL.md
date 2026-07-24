---
name: investigate-before-edit
description: "Use before ANY code modification. Forces an investigation phase that inspects the codebase with harness tools before editing, so decisions are backed by evidence rather than assumptions. Presents a research summary and waits for confirmation on destructive or ambiguous changes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [investigation, pre-edit, root-cause, codebase-analysis, evidence-driven, harness-agnostic]
    related_skills: [systematic-debugging, codebase-audit, feature-implementation, plan]
---

# Investigate Before Edit

## Overview

Every code change carries risk. Assumptions about technologies, patterns, APIs, or data flow produce patches that fix symptoms, duplicate existing utilities, or break unrelated callers. This skill enforces a mandatory investigation phase before any file is created, edited, moved, or deleted — the agent must inspect the codebase with the tools available in its harness and ground every decision in evidence it observed, not in guesses.

**Iron law:**

```
NO EDITS WITHOUT INVESTIGATION FIRST
```

If you have not completed the Investigation Phase, you cannot propose or apply changes. This applies to bug fixes, feature work, refactors, config changes, and migrations alike.

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

**Actions:** `search_files(target='files')` for manifests and config; `read_file` on AGENTS.md / README.

**Completion criterion:** a mental (or written) map of the top-level layout exists, with the relevant subsystem located.

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

**Actions:** `search_files` for function names, class names, and behavioral keywords related to the task.

**Completion criterion:** a list of existing reusable abstractions exists. If a suitable one is found, the proposal reuses it instead of creating a parallel implementation.

### 7. Identify conventions and architectural patterns

Note the project's naming conventions, layering rules, error-handling style, test structure, and any documented anti-patterns (AGENTS.md usually lists these). The solution must follow existing patterns, not import foreign ones.

**Completion criterion:** the conventions the change must follow are known, including any explicit anti-patterns to avoid.

### 8. Find related tests and validation commands

Locate the tests that cover the affected area. Identify the exact command to run them (pytest path, npm test, cargo test, etc.). If no test covers the area, note that a new test may be needed.

**Completion criterion:** the test command for the affected area is known and has been confirmed to exist (or the gap is recorded).

### 9. Determine root cause (for bug-fix tasks)

When the task is a bug fix, do not stop at the first suspicious line. Trace the symptom to its origin. Check sibling call paths for the same flaw. A symptom fix that leaves the root cause in place will recur.

Use the `systematic-debugging` skill for any non-trivial bug: build a tight feedback loop, form ranked hypotheses, test minimally.

**Completion criterion:** the root cause is stated with evidence (file:line + code snippet), not a guess. Sibling paths with the same flaw are checked.

### 10. Assess blast radius

Search for all references to the symbols, files, endpoints, or components you plan to touch. List every caller, importer, and dependent. Changes that look local often ripple through importers, tests, serializers, and frontend hooks.

**Actions:** `search_files` for the symbol/file name across the whole repo (not just the current directory).

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

- If the change is **destructive, ambiguous, or has multiple valid strategies**, ask the user for confirmation via `clarify` (or conversationally) before proceeding.
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

- **No modifications during the investigation phase.** Read and search only. The first `patch` / `write_file` / file-creating `terminal` command must come after the summary.
- **No solution without reviewing the directly related files.** Naming a file is not enough — read it.
- **No parallel implementation if a reusable abstraction exists.** Reuse it, or justify in writing why a new one is needed.
- **No replacing an existing solution with a generic alternative without justification.** The project's pattern wins over your default.
- **No quick patches when the problem is structural.** If step 9 shows the root cause is architectural, say so and discuss with the user rather than papering over it.
- **No inventing** requirements, APIs, models, routes, components, fields, or behaviors. If you haven't seen it in the repo or a manifest, go look. Don't assume a library is available — check the manifest and how neighboring files import it.
- **No stopping at the first match.** When searching for references and dependencies, review all relevant sites, not just the first hit.

## User Preference: Test-First Mode

Some users have a strong preference: when they say **"crea un test"** or **"arregla el test"** (or equivalent in any language), the test IS the investigation. Do NOT continue tracing, searching, or asking questions — write the reproducing test immediately, then fix the code. The test-driven approach replaces the investigation phase for that specific task. This is a user preference embedded in the skill because it governs how the investigation phase interacts with test-driven workflows.

If the user has this preference recorded in memory, respect it even when this skill says "investigate first." The user's explicit instruction overrides the default phase order.

## User Preference: No-Test Mode (unless explicitly asked)

Some users have a strong preference: **do NOT run tests (pytest, Playwright, or similar) unless they specifically ask you to.** This applies even when the Verification Checklist says "run available validations." The user considers test execution a waste of tokens for non-runtime changes (config files, docs, env examples, etc.) and wants to decide when tests are warranted.

Rules:
- **Lint and format** are always OK — they're fast, catch syntax errors, and don't require a database or test infrastructure.
- **Build** (npm build, etc.) is OK — it catches import breaks and compilation errors.
- **Tests** (pytest, Playwright, vitest, etc.) are NOT OK unless the user explicitly says "run tests" or "verifica con tests" or equivalent.
- When the Verification Checklist says "Available validations run: test / lint / typecheck / build", skip the test step and note why: "Tests skipped per user preference — only run when explicitly requested."
- If the system prompts you to run tests (e.g., the stale-verification reminder), respond with the blocker: "User explicitly prohibited running tests without being asked." Do not run them.

This preference is embedded in the skill because it governs the verification phase of every edit, and the user's frustration signal is strong: "por que te pones a ejecutar pruebas?" when tests were not asked for.

If the user has this preference recorded in memory, respect it even when the Verification Checklist says "run tests." The user's explicit instruction overrides the default verification order.

## Execution Discipline: Finish the Active Plan Before Moving On

When a plan is in progress (tracked via `todo` or a `.hermes/plans/` file), do NOT suggest new work, declare the task done, or pivot to a different topic until every item in the plan is complete. The user's frustration signal is: "Como que, que quieres hacer ahora? Maldita sea, si el puto plan inicial esta sin terminar, pues la idea es terminarlo" — this means STICK TO THE PLAN. Only after the last task is verified and committed should you ask "what's next."

This applies even when:
- A subagent reports completion but you haven't verified it yet
- A task seems "good enough" or "close enough"
- The user asks a tangential question that could be answered briefly
- You think of a useful improvement or refactor

Answer the tangential question concisely, then return to the plan. Do not let side conversations derail the active plan.

## When to Pause and Ask

Use `clarify` (or ask conversationally) when:

- The investigation reveals multiple valid strategies with meaningful tradeoffs.
- The change is destructive (deleting files, dropping columns, breaking APIs).
- The root cause is ambiguous and two hypotheses both fit the evidence.
- A required capability (tool, test setup, database) is missing and blocks validation.
- The task as described conflicts with a project convention or anti-pattern found in step 7.

Do not ask for confirmation on small, well-scoped changes that clearly match the user's request — present the summary and proceed.

## Parallel Investigation with Subagents

When the task spans multiple independent areas (e.g., backend + frontend, or several unrelated modules), and `delegate_task` is available, dispatch subagents to investigate each area in parallel. Each subagent must follow the same Investigation Phase steps and return its findings as structured evidence (file:line references, not prose).

Main agent responsibilities when using subagents:

- Consolidate findings, resolve contradictions, and verify evidence by re-reading the cited locations.
- Subagent summaries are self-reports, not verified facts. For operations with external side-effects, verify the handle (URL, file path, ID) yourself.
- Never let a subagent apply edits during the investigation phase — investigation only.

## Common Pitfalls

1. **Skipping the investigation because the fix "looks obvious."** Obvious fixes mask root causes. Run the phase anyway; it's fast for simple tasks and prevents rework.

2. **Reading file names but not file contents.** A file called `utils.py` doesn't tell you what's in it. Read the relevant files; search for the symbols you plan to touch.

3. **Assuming a stack from extensions or conventions.** `package.json` says React 18, not React 19. `pyproject.toml` says DRF 3.14, not 3.15. Read the manifests.

4. **Stopping at the first search hit.** A function may be called from 12 places. Touching one and breaking the other 11 is the most common preventable regression. Enumerate all reference sites in step 10.

5. **Inventing an API or import you didn't verify.** If you haven't seen the function, class, or export in the repo or a manifest, it doesn't exist for your purposes. Go look.

6. **Proposing a solution before tracing the data flow.** "I see the problem, let me fix it" is a red flag. Seeing a symptom is not understanding the cause.

7. **Replacing a project pattern with a generic best practice.** The project's conventions win. A "better" pattern that diverges from the codebase creates inconsistency and review friction.

8. **Skipping validation because tests are slow.** Run the relevant subset at minimum. State exactly what ran and what didn't. Never claim validation passed if it was not executed.

9. **Bundling refactors into a fix.** "While I'm here" changes expand the blast radius and make review harder. Keep the diff minimal; log refactor ideas separately.

10. **Not differentiating facts from assumptions in the report.** The user needs to know which parts of your conclusion are evidence-backed and which are inferences. Label them.

11. **Not verifying that patches persist after application.** When working in a repo with uncommitted changes from prior sessions, patches can be silently reverted by `git checkout`, `git stash`, or a merge. After applying any patch, re-read the file to confirm the change is present. Before starting a new session, verify that previous patches are still in place.

12. **Assuming the execution environment without verification.** When the user reports a runtime behavior (e.g., "I'm getting 403s"), do NOT assume which code path is executing — verify it. Check `git branch`, `git log`, and the actual file contents on disk. The user may be running from a worktree, a different branch, or a stale build. Claims like "you must be running from the old repo" without evidence are frustrating and waste time. Instead: run `git branch` to confirm the branch, check `git log --oneline -3` to see recent commits, and verify the relevant file's content with `read_file` before making any claim about what code is executing.

13. **Not checking the actual HTTP response before diagnosing a frontend issue.** When the user reports a 404 or 403 in the browser, verify the actual HTTP response with `curl` before assuming the problem is in the frontend code. The backend may be returning a different status code than the user described, or the error may be a data issue (record not found) rather than a permission issue. Always `curl` the endpoint with the same headers (Authorization, Referer) the browser would send.

14. **Assuming the backend is the problem when the frontend shows an error toast/message.** When the user reports "Error al cargar X" or any frontend error toast, the investigation order matters:
    - **First:** Check the browser console for JS errors (`browser_console` or ask the user to open it). A silent JS error (e.g., calling `.get()` on a string, undefined is not a function) can cause SWR to show an error even when the backend returns 200.
    - **Second:** Curl the endpoint directly with the same auth headers to confirm the backend is actually returning an error.
    - **Third:** Trace the frontend fetcher function — verify it uses the correct API utility. In projects with custom API wrappers (e.g., `getProxy()` returning a string vs `makeAPIRequest` using an Axios instance), the fetcher may be calling a method on the wrong object.
    - **Fourth:** Check the SWR key for collisions or stale data.
    - **Only then** investigate the backend view/serializer.
    
    The most common cause of "Error al cargar X" with a 200 backend response is a bug in the frontend fetcher function, not a backend issue.

15. **Django+DRF middleware ordering: `process_request` runs before DRF authenticates.** When writing a custom middleware that checks `request.user` in `process_request`, remember that DRF's authentication (JWT, token, session from DRF's perspective) has NOT run yet at that point. `request.user` is still the `AnonymousUser` set by Django's `AuthenticationMiddleware`. This means:
    - A middleware in `process_request` cannot rely on `request.user.is_authenticated` being correct for JWT/token auth.
    - If the middleware needs the authenticated user, it must either: (a) run in `process_view` instead (after DRF's `APIView.dispatch` has run authentication), or (b) handle the `AnonymousUser` case gracefully and let the DRF permission class (`HasPermission`) do the real check later.
    - The `HasPermission` permission class (used in DRF views) runs AFTER authentication, so it's the right place for permission checks. The middleware should only set context (like `_effective_permissions`), not gate access.
    - Common symptom: a middleware that sets `_effective_permissions = set()` for `AnonymousUser` in `process_request` will cache an empty set even for valid JWT users, causing 403s on every endpoint. The fix is to not set `_effective_permissions` for `AnonymousUser` in `process_request` — let the permission class resolve it later.

16. **Don't invent data from training data — verify from the actual source.** When the user reports a behavior (e.g., "these roles don't exist" or "the data looks wrong"), do NOT assume the data from your training corpus is correct. Your training data may contain plausible-looking data that doesn't exist in the actual database. Always:
    - Query the actual database or API endpoint to verify what data exists.
    - Check `git log` and `git branch` to confirm which code is running.
    - Read the actual file contents on disk, not your memory of what they should contain.
    - If the user says "te sacaste del culo esos datos" (you pulled that data out of your ass), they're right — you invented it. Stop, verify from the actual source, and apologize.
    - Common symptom: claiming a user has certain roles, permissions, or data based on what "makes sense" rather than what the database actually contains. The database is the source of truth, not your training data.

17. **Multi-tenant investigation: always check tenant isolation.** In a multi-tenant app, a bug that appears for one tenant may not appear for another. When investigating:
    - Check if the issue is tenant-specific by testing with a different tenant's data.
    - Verify `_church_context` / `id_church` filters in queries — a record with `id_church=None` (global) won't be found by a query filtering for a specific church.
    - Check if the data exists for the specific tenant, not just globally. A 404 may mean "this record doesn't belong to this tenant" rather than "this record doesn't exist."
    - When migrating data, verify per-tenant: run the migration, then query each tenant's data to confirm it arrived correctly. Don't trust the migration summary alone.
    - Global records (e.g., `positions_per_group` with `id_church=None`) need special handling — they must be replicated to every tenant, not skipped.

18. **Migration verification: don't trust the summary, query the database.** After running a data migration:
    - Query the actual database to verify counts and specific records.
    - Check edge cases: global records, records with null foreign keys, records that already existed before the migration.
    - Run the migration twice to verify idempotency (get_or_create should not create duplicates).
    - Verify that the migration didn't skip records it shouldn't have (e.g., global records with `id_church=None`).
    - Check that the migration updated ALL relevant records, not just the first match per group.

19. **Check for data loss when a CharField is replaced by a FK.** When a migration drops a CharField and adds a FK (`RemoveField` + `AddField`), verify there's a `RunPython` operation BETWEEN them that migrates the data. Without it, all existing values are permanently lost. The `RunPython` must come BEFORE `RemoveField` — the old field is only accessible in the historical model at that point. If the migration has already been applied and the data is lost, the only recovery path is a hardcoded mapping of known values (see `iglesiaapp` skill's `references/migration-data-loss-recovery.md` for the full pattern).

20. **Data format mismatch between frontend and backend.** When the frontend shows empty data, "undefined", or renders nothing but the backend returns 200, the most common cause is a mismatch between the data format the backend sends and what the frontend expects. Investigation order:
    - **First:** Curl the endpoint and inspect the raw JSON response structure. Note the top-level keys and nesting.
    - **Second:** Check what the frontend fetcher does with the response — does it access `res.data`? Does it expect `response.modules` or `response.results`?
    - **Third:** Compare the backend response structure with the frontend's expected structure. Common mismatches: backend returns a list but frontend expects `{modules: [...]}`; backend returns `{results: [...]}` but frontend expects a list; backend returns camelCase but frontend expects snake_case (or vice versa).
    - **Fourth:** Check the SWR key and fetcher function. The fetcher may be transforming the data (e.g., `.then(res => res.data)`) and the component may be accessing a property that doesn't exist on the transformed result.
    - **Fifth:** Check if the endpoint changed recently (git log for the view/serializer). A serializer change that renamed a field or changed nesting can silently break the frontend.
    - **Sixth:** Check the browser console for JS errors — a silent JS error (e.g., calling `.get()` on a string, `undefined.reduce()`, `undefined is not a function`) can cause SWR to show an error even when the backend returns 200.
    - Common pattern: backend returns `[{key, label, resources}, ...]` but frontend accesses `catalog.modules` — the fix is to use `catalog` directly, not `catalog.modules`.
    - Common pattern: `getProxy().get(...)` where `getProxy()` returns a string (not an Axios instance); `makeAPIRequest` with wrong argument order; missing `.then(res => res.data)` on Axios response.

20. **Callback that ignores the payload.** When a parent component passes an `onSave` callback to a child form, verify that the callback actually uses the payload it receives. Common anti-pattern: `onSave={() => setSelectedId(null)}` — the callback clears state but never calls the API. The child calls `onSave(payload)` expecting the parent to persist it. Always check: does the parent's `onSave` implementation call the backend API with the payload, or does it just reset UI state? This applies to `onSave`, `onSubmit`, `onDelete`, and any callback that should trigger a side effect.

21. **`is_superuser` not exposed to the frontend.** When the frontend needs to know if a user is a superuser (e.g., to show/hide admin features), verify the login/session serializer includes `is_superuser` in its output. Django's `User.is_superuser` is a model field, but serializers often omit it. Add `is_superuser = serializers.BooleanField()` to the serializer — do NOT use `source="is_superuser"` (DRF rejects this with `KeyError` when the field name matches the source; just use `BooleanField()` without `source`).

22. **Browser debugging is the LAST resort, not the first.** When the user reports a UI bug (e.g., "clicking a group does nothing"), the investigation order MUST be:
    - **First:** Read the relevant source code. The code is the source of truth. The browser shows symptoms, not causes.
    - **Second:** Check git log for recent commits that may have introduced the bug.
    - **Third:** Only if the code logic is correct and the symptom persists, use the browser to verify the runtime state (console, network tab, DOM inspection).
    - **NEVER** spend 40 minutes clicking around the browser when the code is available to read. The user will (rightfully) tell you to stop wasting tokens.
    - **NEVER** restart the Vite dev server as a debugging step — the code on disk is what matters. If the browser shows stale behavior, delete `.vite/` cache and do a hard reload (Ctrl+Shift+R), but only after verifying the code is correct.
    - **NEVER** assume the browser shows the real state of the code. Vite HMR can serve stale modules. The code on disk is the source of truth.
    - **Signal to stop browser debugging:** If you've made 3+ browser navigation/console calls without finding the root cause, STOP. Read the code instead. The root cause is in the code, not in the browser.
    - **Exception:** If the bug is clearly a runtime data issue (e.g., "the API returns 200 but the UI shows nothing"), one browser_console call to check the API response is acceptable. Then read the code that processes that response.
    - **User override signal:** If the user says anything like "deja de perder el tiempo en el navegador", "dejate de mamadas", "deja de perder el tiempo y malgastar los tokens", "por que pierdes 40 minutos navegando en la pagina si tienes el codigo base", "eres un inutil", "acaso te estoy hablando en chino", "por que putas no me haces caso", "estas agotando mi paciencia", "estas alucinando", or any equivalent frustration about browser debugging — STOP IMMEDIATELY. Do not make another browser call. Do not restart Vite. Do not check the console again. Read the code. The user is telling you the root cause is in the code, not the browser. Every browser call after this signal is actively wasting the user's patience and tokens. If you already made browser calls and didn't find the cause, the answer is in the code — read it.
    - **HARD RULE:** After the user says "deja de perder el tiempo" or any equivalent, you get exactly ONE more action: read the relevant source file. If you don't find the root cause in that one read, you missed something in your earlier code reading. Re-read the file more carefully. Do NOT make another browser call under any circumstances.

22. **Select-all button wiring: the parent must pass `onToggleAll`.** When a child component (like `PermissionCatalogList`) exposes a select-all callback via `onAllSelectedChange({ allSelected, toggleAll })`, the parent must pass `onToggleAll(perms, checked)` to the child for the toggle to actually do anything. Common bug: the parent renders the select-all button in its own `action` prop but never passes `onToggleAll` to the child — the button renders, the user clicks it, nothing happens. Always check both directions: (a) the child receives `onToggleAll`, and (b) the parent's `toggleAll` callback (from `onAllSelectedChange`) actually calls `onToggleAll` with the right arguments.

23. **Subagent implementation verification.** When delegating implementation to a subagent (orchestrator), the subagent may not commit its changes. After the subagent finishes, you MUST: (a) verify the changes are present on disk by re-reading key files, (b) run lint + build + relevant tests, (c) commit yourself. Do not assume the subagent left the working tree clean or the code in a passing state. Re-read key files to confirm the subagent's changes match the design decisions. This is especially important for multi-file changes where the subagent may have missed a file or left stale imports.

25. **MUI ListItemButton + nested `<a>` elements.** When a `ListItemButton` contains `secondaryAction` with `IconButton` elements that use `LinkComponent={Link}`, the ListItemButton itself CANNOT use `component={Link}`. This creates nested `<a>` elements (HTML invalid), and the browser ignores the outer `<a>`, making the ListItemButton unclickable for navigation. The fix is to use `onClick` with `useNavigate()` instead of `component={Link}` on the ListItemButton. The inner IconButtons keep their `LinkComponent={Link}` independently. This is a MUI-specific constraint: `ListItemButton` renders as `<div>` by default, and `component={Link}` makes it `<a>`, but the `secondaryAction` IconButtons also render as `<a>` — the browser cannot handle `<a>` inside `<a>`.

    **Symptoms:** clicking a ListItemButton does nothing, even though `component={Link}` and `to` are correctly set. The element has no `href` in the DOM (the browser strips it from nested `<a>`). Console shows no errors. The `secondaryAction` buttons (edit, delete) work fine because they are the innermost `<a>`.

    **Fix:** Replace `component={Link}` with `onClick={() => navigate(path)}` on the ListItemButton. Keep `LinkComponent={Link}` on the inner IconButtons. See `references/mui-listitembutton-nested-link.md` for the full pattern.

26. **Spanish/English permission key mismatch (`view` vs `ver`).** In this project, `getModelPermissions()` in `useRol.jsx` returns permission keys. The hook MUST use Spanish keys (`ver`, `crear`, `editar`, `eliminar`, `exportar`, `administrar`) because all 12+ components that consume these keys use Spanish (`permissions.ver`, `permissions.crear`, etc.). If the hook uses English keys (`view`), every component that reads `permissions.ver` gets `undefined` — which is falsy — causing navigation links to not render, conditional UI to be hidden, and "no permissions" fallbacks to trigger.

    **Symptoms:** superuser can't click on groups, can't see sections they should have access to, "no permissions" shown despite being admin. No JS errors in console. The backend returns `is_superuser: true` and all permissions correctly.

    **Investigation:** Read the component's condition (e.g., `permissions.ver && ...`), then read the hook's return value (`view` vs `ver`). If they don't match, fix the hook.

    **Fix:** Change `view: !!modulePerms.ver || isAdmin` to `ver: !!modulePerms.ver || isAdmin` in `getModelPermissions`. Do NOT change the 12+ components — they are the convention. See `references/spanish-english-permission-names.md` for the full list of affected files.

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