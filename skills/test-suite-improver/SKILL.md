---
name: test-suite-improver
description: "Use when the user wants to audit a project's test suite and improve it — analyze codebase + tests, evaluate quality, select a work mode, plan, write/fix/delete tests, and validate. Harness-agnostic: discovers available tools at runtime and adapts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [testing, test-suite, quality, audit, harness-agnostic, refactoring]
    related_skills: [codebase-audit, test-driven-development, requesting-code-review, systematic-debugging]
---

# Test Suite Improver

Audit a project's test suite, evaluate the quality of every existing test, then improve the suite by writing valuable tests, fixing broken ones, and removing ones that add no value. Harness-agnostic: discovers available tools at runtime and adapts. Does NOT assume any framework, runner, or language — inspects the project first.

## When to Use

- User asks to "improve the tests", "review the test suite", "audit tests", "make tests better", or "rebuild the test suite".
- User wants to identify tests that don't assert, are redundant, fragile, obsolete, or always-pass.
- User wants to increase confidence in a project by improving test quality (not raw coverage).
- User wants a testing strategy for a project with weak or missing tests.

Don't use for:
- Writing a single test for a known bug (use `test-driven-development` instead).
- Reviewing only git diffs (use `requesting-code-review` instead).
- Debugging a specific failing test (use `systematic-debugging` instead).
- Full codebase security/performance audit (use `codebase-audit` instead).

## Architecture: Core + Adapters

This skill separates harness-independent logic from harness-specific tool binding.

**Core logic** (this file): project discovery, test evaluation methodology, work-mode selection, planning, test generation, validation, reporting. Written entirely in terms of *capabilities* — never names specific tools.

**Harness adapter** (loaded from `references/harness-adapters.md`): maps capabilities to concrete tools available in the current environment. Selected at runtime based on detected harness.

Capabilities the core depends on (adapter must provide or flag as missing):

| Capability | Purpose |
|---|---|
| `file_read` | Read file contents (source + tests) |
| `file_search` | Search file contents (regex/grep) |
| `file_find` | Find files by name/glob |
| `file_write` | Edit/create test files |
| `dir_list` | List directory contents |
| `cmd_exec` | Execute shell commands (run tests, coverage, linters) |
| `git_query` | Query git history/branches |
| `web_search` | Search the web (best practices for detected frameworks) |
| `web_extract` | Extract web page content (official docs) |
| `user_ask` | Ask user structured questions (mode selection, confirmations) |
| `subagent_spawn` | Delegate tasks to subagents (parallel analysis) |
| `task_manage` | Manage a todo/task list |
| `state_persist` | Persist state across interruptions |
| `html_open` | Open an HTML file in a browser |

See `references/harness-adapters.md` for per-harness bindings and the fallback generic adapter.

## Phase 1: Tool Discovery & Adapter Selection

1. Detect which tools are available in the current environment. Do NOT assume any tool exists.
2. For each capability in the table above, determine: available (which tool), or missing.
3. Select the matching harness adapter from `references/harness-adapters.md`. If no specific match, use the generic adapter.
4. Record the capability map. Missing capabilities are logged as limitations that affect the workflow.
5. **Completion criterion**: every capability is classified as available (with concrete tool name) or missing (with impact noted).

## Phase 2: Project Discovery

1. Find the repository root (look for `.git`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `requirements.txt`, `composer.json`, `Gemfile`, `pubspec.yaml`, etc.).
2. Map the directory structure using `file_find` and `dir_list`. Exclude: `node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `.venv`, `venv`, `target`, `.next`, `coverage`, and any user-specified exclusions.
3. Identify languages, frameworks, build tools, test runners, and infrastructure from config files and dependency manifests. Extract exact versions from lockfiles when present.
4. Identify test directories and test file patterns. Detect: test runner (pytest, jest, vitest, go test, cargo test, rspec, junit, xunit, playwright, cypress, etc.), assertion library, mocking library, test database setup, CI config.
5. Locate test infrastructure: fixtures, factories, mocks, helpers, seed data, test settings, conftest files, setup/teardown hooks.
6. Analyze the application architecture: main modules, entry points, API endpoints, background jobs, external integrations, database models, business rules.
7. Identify critical flows: authentication, authorization, data access, payment, external API calls, file processing, scheduled jobs, message queues.
8. **Completion criterion**: a structured project map exists with technologies, versions, module list, entry points, test setup, test infrastructure inventory, and critical-flow list.

## Phase 3: Initial Test Suite Baseline

1. Run the test suite using `cmd_exec` with the project's test command. Capture: pass count, fail count, skip count, duration.
2. If the test command is unknown, detect it from config files. Common patterns:
   - Python: `pytest`, `python -m pytest`, `tox`, `nox`, `python manage.py test`
   - Node: `npm test`, `yarn test`, `npx jest`, `npx vitest`, `npx mocha`, `npx playwright test`
   - Go: `go test ./...`
   - Rust: `cargo test`
   - Ruby: `bundle exec rspec`, `bundle exec minitest`
   - Java: `mvn test`, `gradle test`
   - .NET: `dotnet test`
3. If the suite cannot run (missing deps, missing DB, etc.), record the blocker and the exact command the user must run. Continue with static analysis.
4. Run coverage analysis if a coverage tool is available (pytest-cov, coverage.py, jest --coverage, go test -cover, cargo tarpaulin, etc.). Record coverage numbers per file/module. Coverage is a signal, not the goal.
5. Record the initial state: tests passed, failed, skipped, errors, coverage %, duration, any blockers.
6. **Completion criterion**: initial baseline is recorded with exact numbers and command outputs (or documented blockers with exact commands for the user).

## Phase 4: Evaluation of Existing Tests

Review every test file. For each test, classify it using the checklist in `references/test-smells-checklist.md`. Look for:

1. **No useful assertions**: tests that call code but don't assert meaningful outcomes, or assert only that no exception was thrown.
2. **Implementation-detail testing**: tests that verify internal method calls, private state, or structural details that would break on a valid refactor.
3. **Duplicates**: tests that verify the same behavior as another test (same inputs, same assertions, different name).
4. **Fragile tests**: tests that depend on execution order, shared mutable state, the current date/time, external services, or environment variables.
5. **Excessive/incorrect mocking**: tests that mock the system under test, mock everything so the test validates only the mock, or mock types that don't match the real interface.
6. **Tautological tests**: tests that always pass regardless of whether the code works (e.g., `assert True`, `assert result is not None` without checking value).
7. **Obsolete tests**: tests for code that no longer exists or behaves differently (imports that would fail, renamed functions, changed signatures).
8. **Slow tests without value**: tests that take >5s but could be replaced by a faster equivalent.
9. **Missing coverage**: important functionality, error paths, validations, permissions, edge cases that have no tests.

Do NOT flag a test for removal just because it is simple or has low coverage. Each removal must be justified by: lack of value, redundancy, or incompatibility with current behavior.

For each test, record: file, test name, classification (keep / fix / remove / split), reason, evidence.

**Completion criterion**: every test file has been reviewed; a classified test inventory exists with evidence for every non-keep decision.

## Phase 5: Technical Research

For each detected test framework + version:

1. Use `web_search` and `web_extract` to consult official documentation and best-practice guides for the exact framework version.
2. Research: recommended test patterns, fixture strategies, mocking guidelines, integration vs unit test boundaries, coverage tools, common anti-patterns, async testing patterns, parameterized test patterns.
3. Research framework-specific issues: known flaky test causes, fixture isolation problems, test database strategies, parallelization support and pitfalls.
4. Build a temporary knowledge base of framework-specific best practices.
5. Record all sources consulted.
6. If `web_search` is unavailable: rely on built-in knowledge of the frameworks, note the limitation, and reduce confidence on framework-specific recommendations.
7. **Completion criterion**: a framework-specific best-practice reference exists for each test technology in the project, with sources cited.

## Phase 6: Work Mode Selection

Before modifying any test file, ask the user — using `user_ask` if available — to select a work mode:

**Mode 1 — Improve the current suite**
- Keep useful tests.
- Fix broken tests.
- Remove only tests that are clearly redundant, invalid, or obsolete.
- Add missing cases.

**Mode 2 — Rebuild the suite from scratch**
- Remove current tests.
- Keep only reusable infrastructure that is still valid (factories, fixtures, helpers, test settings).
- Design and create a new suite based on actual project behavior.

**Mode 3 — Analysis only**
- No file modifications.
- Deliver a report with detected problems and a proposed testing strategy.

Mode 2 requires explicit confirmation via `user_ask` because it deletes the entire test suite. Present the consequences clearly: all test files will be deleted, only infrastructure preserved, the new suite will be built from the project's actual behavior.

If `user_ask` is unavailable, ask in plain conversation but require an explicit text confirmation for Mode 2.

**Completion criterion**: user has explicitly selected a mode; for Mode 2, explicit confirmation has been recorded.

## Phase 7: Planning

Create a prioritized test plan. For each item:

1. **Functionality**: what behavior must be tested.
2. **Risk**: impact if this behavior breaks (critical / high / medium / low).
3. **Test type**: unit, integration, contract, API, component, end-to-end, snapshot, property, regression.
4. **Files**: which test files to create, modify, or delete.
5. **Infrastructure**: fixtures, factories, helpers, mocks, test DB setup needed.
6. **Dependencies**: what must exist before this test (other tests, infra, fixtures).
7. **Order**: suggested implementation sequence.

Priority is based on impact × risk, not coverage percentage. Critical business rules and error paths come first.

Present the plan to the user via `user_ask` (or conversationally) for confirmation before executing.

**Completion criterion**: a prioritized plan exists and the user has confirmed it (or adjusted it).

## Phase 8: Test Generation & Modification

Follow the plan. Apply the patterns from `references/test-design-patterns.md` for the detected framework. New and modified tests must:

1. **Validate observable behavior and business rules** — not implementation details.
2. **Cover happy paths, errors, validations, and edge cases** — not just the success route.
3. **Be deterministic, isolated, and repeatable** — no hidden order dependencies, no shared mutable state.
4. **Avoid unnecessary environment dependencies** — use test databases, in-memory adapters, or containerized services.
5. **Use mocks only when they add value** — don't mock the system under test; mock external boundaries.
6. **Use descriptive names** — the name should describe the behavior being tested, not the implementation.
7. **Follow language and framework conventions** — match existing style, naming, structure.
8. **Reuse factories, fixtures, and helpers** — don't duplicate setup logic.
9. **Do not test third-party dependencies directly** — test your code's interaction with them.
10. **Include regression tests for known bugs** when context is available (git history, issue tracker, comments).
11. **Maintain a reasonable balance** between unit, integration, and end-to-end tests.

Do NOT generate trivial tests just to increase coverage. A test that asserts `result is not None` without checking the value is not a test.

For Mode 2 (rebuild): delete test files first (preserving infrastructure), then write the new suite test-by-test following the plan.

For Mode 1 (improve): fix broken tests first, then remove flagged tests, then add missing cases.

For Mode 3 (analysis only): skip this phase entirely.

**Subagent strategy** (when `subagent_spawn` available): split work by module. Each subagent receives: project map, framework best practices, the plan, the test smells inventory, and the module's source files. Each subagent returns: test files created/modified, with summaries. The main agent coordinates to avoid duplicate tests and incompatible fixtures.

**Completion criterion**: all planned test files have been created/modified/removed; no planned item is pending.

## Phase 9: Validation

1. Run the new/modified tests individually to verify they pass.
2. Run the full test suite to verify no regressions.
3. **Mutation verification**: when safe, deliberately break the behavior a test validates (comment out a line, invert a condition, return wrong value) and confirm the test fails. Then revert. This proves the test actually catches the bug. Do this for a sample of the new/modified tests, not necessarily all.
4. Run linters, type checkers, and other validators available in the project.
5. Run coverage analysis again. Compare before/after.
6. Identify slow tests (>5s), flaky tests (pass on retry but fail intermittently), or tests with order dependencies.
7. Confirm the application still builds/starts — the test changes must not break production code.
8. If any command cannot run, state the cause and provide the exact command for the user.

Classify validation result as: **passed** (all checks ran and passed), **failed** (one or more checks failed), **partial** (some passed, some couldn't run), **not_run** (validation could not execute).

NEVER claim validation passed if it was not executed. State exactly what ran, what passed, what failed, and what couldn't run.

**Completion criterion**: validation result is classified and all executed check results are recorded.

## Phase 10: Final Report

Deliver a summary containing:

- Technologies and tools detected (languages, frameworks, test runner, versions).
- Initial state of the suite (pass/fail/skip counts, coverage, duration).
- Work mode selected by the user.
- Tests created, fixed, kept, and removed (with file paths).
- Justification for every removal.
- Functionality now covered.
- Risks that remain without coverage.
- Validation results (what ran, what passed, what failed, what couldn't run).
- Coverage change (before → after, per module).
- Pending issues and limitations (missing tools, unverified hypotheses).
- Recommendations for maintaining the suite in the future.

If `file_write` is available, optionally generate a Markdown or HTML report using `references/report-template.md` and save it in the repo root or a temp path. If `html_open` is available, open it.

**Completion criterion**: the user has received the full report (inline and/or file).

## State & Resumption

When `state_persist` is available, record after each phase:

- Capability map (available/missing tools).
- Project map (technologies, versions, modules, test setup).
- Initial baseline (test results, coverage).
- Test inventory (classified: keep/fix/remove/split, with evidence).
- Work mode selected.
- Plan (prioritized items with status).
- Validation results.
- Errors and limitations.

This enables resuming an interrupted run without re-analyzing completed phases.

When `state_persist` is unavailable: keep findings in context and track progress via `task_manage`. Acknowledge that resumption is limited.

## Subagent Strategy

When `subagent_spawn` is available, parallelize these independent workstreams:

| Subagent | Task | Input | Output |
|---|---|---|---|
| Architecture analyst | Phase 2 (project discovery) | Repo root | Project map |
| Test evaluator | Phase 4 (test review) | Project map + test files | Classified test inventory |
| Best-practices researcher | Phase 5 (technical research) | Detected frameworks + versions | Framework best-practice reference |
| Test implementer (per module) | Phase 8 (test generation) | Plan + source + best practices | Test files + summaries |
| Validator | Phase 9 (validation) | All test files | Validation results |

Phases 2, 4, and 5 can run in parallel. Phase 8 implementers can run in parallel by module. Phase 9 runs after all implementers finish.

The main agent: consolidates, deduplicates, resolves conflicts, ensures no duplicate tests, ensures shared fixtures are compatible.

When subagents are NOT available: process phases sequentially within one agent using the same input/output formats.

## Context Management for Large Repos

- Process test files in batches, never load all at once.
- Write intermediate results to state file after each phase.
- Create module/test-file summaries after analysis, then drop raw code from context.
- Prioritize: critical business logic, API endpoints, auth, data access > utilities, config, docs.
- Use subagents to keep each agent's context focused.
- Re-read a file before modifying it (it may have changed).

## Restrictions

- Do NOT remove tests without prior analysis (Phase 4).
- Do NOT delete the entire suite without explicit user confirmation (Phase 6, Mode 2).
- Do NOT modify production code solely to make tests pass — unless a real bug is detected and the user authorizes the fix.
- Do NOT use coverage as the sole quality metric.
- Do NOT hide failing tests or disable them without justification.
- Do NOT assume commands, frameworks, or tools before inspecting the project.
- Do NOT make mass changes without explaining the scope first (Phase 7 plan confirmation).
- Do NOT generate trivial tests to inflate coverage.

## Common Pitfalls

1. **Assuming tools exist.** Always discover first. A missing `cmd_exec` means no tests run. A missing `web_search` means lower confidence on framework-specific patterns. Record the limitation, don't hide it.

2. **Assuming the test runner.** Never guess `pytest` or `jest`. Detect from config files. Run the exact command the project uses.

3. **Removing tests without evidence.** Every removal must cite the specific smell (duplicate, tautological, obsolete) with the test name and file. "Looks simple" is not a reason.

4. **Claiming validation passed without running it.** Never. State exactly what ran, what passed, what failed, what couldn't run.

5. **Testing implementation details.** Tests that assert internal method calls break on valid refactors. Test observable behavior instead.

6. **Inflating coverage with trivial tests.** `assert result is not None` adds coverage but no value. Each test must assert a meaningful outcome.

7. **Not running mutation verification.** A test that always passes proves nothing. Break the code, confirm the test fails, revert. At least for a sample.

8. **Skipping the initial baseline.** Without a "before" snapshot you can't measure improvement. Always run the suite first (or document why it couldn't run).

9. **Ignoring framework-specific best practices.** pytest fixtures ≠ jest beforeEach. Research the exact framework before writing tests.

10. **Parallel subagents writing incompatible fixtures.** Coordinate shared infrastructure. Two subagents creating `conftest.py` entries that conflict will break the suite.

## Verification Checklist

- [ ] Tool discovery completed; capability map recorded with missing tools noted
- [ ] Harness adapter selected and loaded
- [ ] Project map complete: technologies, versions, modules, test setup, test infrastructure
- [ ] Initial baseline recorded (test results + coverage, or documented blocker)
- [ ] Every test file reviewed; classified inventory with evidence for non-keep decisions
- [ ] Framework-specific best practices researched with sources cited
- [ ] User selected work mode (Mode 2 has explicit confirmation)
- [ ] Plan created and confirmed by user
- [ ] All planned test files created/modified/removed
- [ ] Validation run: each check classified as passed/failed/not_run
- [ ] Mutation verification done on a sample of new/modified tests
- [ ] Coverage before/after compared
- [ ] Final report delivered (inline and/or file)
- [ ] State file updated (when persistence available)
- [ ] Limitations section in report: missing tools, unverified items, pending issues