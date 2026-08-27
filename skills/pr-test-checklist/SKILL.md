---
name: pr-test-checklist
description: "Use when the user asks for a manual testing checklist for one or more Pull Requests ('generar checklist de pruebas', 'crear plan de testing para este PR', 'qué tengo que probar de este cambio') before merge. Analyzes the real diff and source code of each PR to produce actionable, traceable tests free of assumptions. Does not perform full regression — only validates what changed and its direct side effects."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, pull-requests, checklist, qa, manual-testing, code-review, github]
    related_skills: [issue-enrichment, investigate-before-edit, test-suite-improver]
---

# PR Test Checklist

## Overview

When one or more Pull Requests arrive for review, the team needs to know what to test manually — which views to open, which flows to exercise, which edge cases to verify. Doing it from memory or reading only the PR title produces incomplete validations and production bugs.

This skill analyzes the real changes of each PR (diff, modified files, affected source code) and generates a manual testing checklist organized by module, with navigable links to views when they can be generated. Every checklist item is traceable to the PR that originated it and backed by evidence from the code — not by assumptions.

The deliverable is a Markdown document ready for a QA or developer to execute the tests without having read the code.

## When to Use

- The user asks to "generar checklist de pruebas", "crear plan de testing para este PR", "qué tengo que probar de este cambio", or the English equivalents ("generate a testing checklist", "what should I test in this PR").
- One or several PRs arrive and a manual testing guide is needed before merge.
- The user wants to validate that the changes don't break adjacent flows without doing a full regression.
- The user wants traceability: to know exactly which test covers which change of which PR.

Don't use for:
- Writing automated tests (unit, integration, e2e) — use `test-suite-improver` for that.
- Code review of the PR — run a diff-based code review instead.
- Debugging a specific bug reported in a PR — investigate and debug it directly.
- Generating documentation for the whole application — this is a change-validation checklist, not a user manual.

## Input

Accept the PRs to analyze from one of these sources, in priority order:

1. **PR number** — `gh pr view <num>` and `gh pr diff <num>`.
2. **PR URL** — extract the number and repo, then `gh pr view`.
3. **Local branch** — if the user names a branch, use `gh pr list --head <branch>` to find the associated PR.
4. **Explicit list** — the user passes several PR numbers separated by comma or space.

If the user does not specify which PRs to analyze, ask. Do not assume "the most recent PR" or "the current branch".

### Information the user must provide

There are data the skill cannot infer from the code or from GitHub. Ask the user when they are needed:

- **Base URL of the testing environment** (e.g. `https://test.myapp.com`). Without it, navigable links cannot be generated.
- **Credentials and roles** required to test certain flows (e.g. "admin", "user with permission X"). The skill lists them as prerequisites; the user must provide the concrete values.
- **Dynamic IDs** for URLs that require an existing record (e.g. `{userId}`). If the user does not provide them, leave the placeholder.
- **PRs to analyze** if they were not provided in the initial input.

Do not invent URLs, routes, permissions, test data, or behaviors that are not backed by the code or by information provided by the user.

## Phase 1: PR data collection

For each PR to analyze:

1. **Get PR metadata** with `gh pr view <num>`. Record: title, description, author, base branch, labels, milestone, and — critically — all PR comments (`gh pr view <num> --comments`). Comments frequently contain design decisions, scope changes, bugs found during review, or author notes that affect what must be tested.

2. **Get the full diff** with `gh pr diff <num>`. Analyze:
   - Files added, modified, and deleted.
   - Lines changed, inserted, and deleted per file.
   - Nature of the change: new feature, bug fix, refactor, configuration change, migration, dependency change.

3. **Classify the modified files** into categories:
   - **Frontend**: components, pages, routes, hooks, styles, assets.
   - **Backend**: models, views/controllers, serializers, services, migrations, configuration.
   - **Infrastructure**: CI/CD, Docker, deploy configs, environment variables.
   - **Dependencies**: changes in `package.json`, `requirements.txt`, `Cargo.toml`, etc.
   - **Documentation**: README, docs, comments.

4. **Identify the affected modules/features** based on:
   - File paths (e.g. `src/modules/users/` → Users module).
   - Names of modified components/views.
   - Affected entities/models.
   - Touched API endpoints.

**Completion criterion:** Each PR has its metadata recorded, full diff, files classified by category, and modules identified. PR comments were read.

### Fallback when `gh` is not available

If `gh` is not installed or not authenticated, use the GitHub API:

```bash
curl -s https://api.github.com/repos/{owner}/{repo}/pulls/{num}
curl -s https://api.github.com/repos/{owner}/{repo}/pulls/{num}/files
curl -s -H "Accept: application/vnd.github.v3.diff" https://api.github.com/repos/{owner}/{repo}/pulls/{num}
curl -s https://api.github.com/repos/{owner}/{repo}/issues/{num}/comments
```

If neither option works, ask the user to provide the diff (pasted or as a file) and the PR metadata.

## Phase 2: Source code analysis

The diff shows what changed, but not why, nor the context around it. This phase investigates the actual source code to understand the impact of the changes.

### 2.1 Read the modified files

For each file in the diff that is not configuration or documentation, read the full file (or the relevant sections). The diff only shows changed lines; the full file reveals:

- What the function/class/component where the change occurred does as a whole.
- What imports and dependencies it has.
- How it relates to the rest of the system.

Do not assume behavior from the file or function name. Read.

### 2.2 Trace the affected flow

For each significant change, follow the execution trace:

- **Frontend**: component → hook/provider → API call → state → rendering. Identify which route shows that component, what props it receives, which user interactions trigger the changed code.
- **Backend**: request → middleware → view/controller → serializer/validator → model → response. Identify the endpoint, HTTP method, parameters, required permissions.
- **Full-stack**: when a PR touches frontend and backend, trace the complete flow to verify that both sides of the contract are consistent.

### 2.3 Identify routes and views

Search for the routes that expose the modified components/views:

- **React Router / Vue Router / Angular Router**: search route files, identify the path and URL parameters.
- **Next.js**: structure of `pages/` or `app/`.
- **Backend**: `urls.py`, `routes.rb`, `web.php`, controller annotations.
- **API**: affected REST or GraphQL endpoints.

For each identified view, build the testing URL if the user provided the base URL. Format: `{base_url}/{route}` with `{parameter}` placeholders for dynamic IDs.

### 2.4 Identify permissions and authorization

Review:

- Permission decorators (Django: `@permission_required`, DRF: `permission_classes`).
- Authentication/authorization middleware.
- Frontend guards (protected routes, role-based rendering conditions).
- Conditional logic that depends on the user's role or permissions.

Every identified permission becomes a test case: "user without permission X should not be able to access".

### 2.5 Identify validations and edge cases

Review:

- Form/serializer validators (required fields, formats, ranges, uniqueness).
- Error handling (try/catch, frontend error states, error messages).
- Empty states (lists without data, null fields, empty relations).
- Business-logic edge cases: boundary values, invalid inputs, race conditions visible from the UI.
- External integrations: if the change touches an external API call, verify what happens when it fails.

**Only include edge cases the code actually contemplates or that the change makes likely.** Do not invent hypothetical scenarios.

### 2.6 Assess blast radius

Search for references to the modified symbols/files/components in the rest of the code. A change in a utility function can affect dozens of callers. Identify which other modules or views depend on the changed code — those views must be tested too.

**Completion criterion:** For each PR, the full affected flow is understood, routes/views are identified with their URLs, permissions and validations are documented, and the blast radius has been assessed.

## Phase 3: Checklist generation

### Generation principles

Every checklist item must be:

1. **Traceable**: includes a reference to the PR that originated it.
2. **Actionable**: a tester who has not read the code must be able to execute it.
3. **Specific**: describes the concrete action, the view where it runs, and the expected result.
4. **Evidence-based**: everything it states comes from the diff or the source code read. Nothing invented.
5. **Scoped**: only tests related to the detected changes and their direct side effects. Previously working functionality is assumed to work — this is change validation, not full regression.

### Checklist structure

Organize by module/feature. Within each module, group by view or flow. Prioritize: high-impact/high-risk flows first, then complementary cases.

Write the checklist in the user's language — including section headings (e.g. a Spanish-language team gets "Checklist de Pruebas", "Módulo", "Vista", "Obligatorias"). The template below shows English headings:

```markdown
# Testing Checklist — PRs #[nums]

**Environment:** {base URL provided by the user}
**PRs analyzed:** #123, #456
**Date:** {generation date}

> ⚠️ **Instructions:** Tests marked 🔴 are mandatory (they cover critical or high-risk changes). Tests marked 🟡 are recommended (edge cases or complementary verifications).

---

## Module: {Module name}

### View: {View name}

**URL:** `{base_url}/{route}`
**Origin:** PR #{num} — {brief description of the change}

**Prerequisites:**
- {required role/permission}
- {required data or prior state}

#### 🔴 Mandatory

- [ ] **{Action}**: {Precise description of what the tester must do.}  
  **Expected result:** {What the tester should observe.}

- [ ] **{Another action}**: {Description.}  
  **Expected result:** {What the tester should observe.}

#### 🟡 Recommended

- [ ] **{Action}**: {Description.}  
  **Expected result:** {What the tester should observe.}

---

## Module: {Another module}
...
```

### Severity classification

- 🔴 **Mandatory**: changes in business logic, permissions, validations, data flows, integrations, API endpoints. If these tests fail, the PR should not merge.
- 🟡 **Recommended**: edge cases, empty states, regression tests in adjacent views affected by the blast radius, UI/style verifications, tests with different roles when the change does not touch permissions directly.

### Item contents

For each item, include when applicable:

| Field | Description |
|---|---|
| **Module/feature** | Area of the application |
| **View/route** | Where the test is executed |
| **URL** | Direct link to the view (with placeholders if IDs are missing) |
| **Prerequisites** | Role, data, prior state needed |
| **Action** | What the tester does, step by step if necessary |
| **Expected result** | What the tester should observe |
| **Edge cases** | Variations of the same test (different inputs, roles, states) |
| **Origin** | PR that motivates this test |

Do not include fields without information — an item does not need all 8 fields if only 4 apply.

### Quality filtering

Before declaring the checklist done, review every item against these criteria:

- Is it backed by evidence from the diff or the code? If not, remove it.
- Is it generic or redundant? Tests like "check the page loads", "verify no console errors" with no concrete relation to a change → remove or rephrase with specificity.
- Is it an unrelated regression? "Test login", "test registration" when the PR doesn't touch auth → remove. Direct effects only.
- Could someone who hasn't read the code execute it? If the action is ambiguous ("review the users module"), rephrase with concrete instructions.

**Completion criterion:** The checklist is complete, organized by module, every item is traceable to its origin PR, there are no generic or invented items, URLs are correct (or use documented placeholders), and the mandatory/recommended classification is consistent.

## Phase 4: Review with the user

1. **Present the checklist** to the user for review. Highlight:
   - Number of tests generated (mandatory and recommended).
   - PRs covered.
   - Modules identified.
   - Any limitations (e.g. "could not determine the URL for module X because the routes file was not found", "placeholders `{id}` need to be replaced with real IDs from the testing environment").

2. **Collect feedback** from the user:
   - Are tests missing that the user considers necessary?
   - Are there tests that don't apply and should be removed?
   - Do the placeholders need concrete values?
   - Is the level of detail adequate?

3. **Iterate** if the user requests adjustments.

4. **Final delivery format** — ask the user:
   - Write the checklist to a Markdown file? (e.g. `pr-test-checklist-{nums}.md`)
   - Publish as a PR comment? (use `gh pr comment <num> --body-file`)
   - Deliver only in the conversation?

Do not publish to GitHub without explicit user confirmation.

**Completion criterion:** The user reviewed and approved the checklist, or requested adjustments that were applied. The delivery format is defined and executed.

## Common Pitfalls

1. **Generating tests based only on the PR title/description.** The title says "Add date filter" but the diff shows pagination was also modified. Without reading the diff and the code, the checklist would be incomplete. Always read the full diff and the modified files.

2. **Inventing URLs, routes, or behaviors.** If the routes file was not found, do not assume the URL is `/users/{id}/edit`. Use placeholders and document the limitation. If the code does not show a certain behavior, do not claim it exists.

3. **Including generic tests unrelated to the changes.** "Verify login works" does not belong in the checklist of a PR that changed date formatting in a report. Every item must trace to a concrete change in the diff.

4. **Turning the checklist into a full regression.** The goal is to validate changes, not re-verify the whole application. If the PR touches 3 files in the Reports module, the checklist covers Reports and the modules that depend on it, not the application's 20 modules.

5. **Not reading the PR comments.** Comments frequently contain critical information: "this only applies to admin users", "the UI change is mobile-only", "I removed validation X because Y". Without reading them, the checklist may include tests for behaviors that no longer exist or omit cases reviewers requested.

6. **Assuming permissions or roles without verifying them in the code.** "Probably only admin can access" is worthless. Read the permission decorators, guards, or middleware. If the code shows no permission restriction, do not invent one.

7. **Not asking when information is missing.** If the testing environment's base URL was not provided, ask. If a test user ID is needed, ask. A checklist full of placeholders without values is less actionable than one where the user provided the data.

8. **Generating redundant tests.** Two items describing essentially the same action with the same expected result confuse the tester. Consolidate or remove the redundant one.

9. **Not checking the blast radius.** A change in a utility function like `formatDate()` can affect 15 views. If you only generate the test for the view mentioned in the PR, the other 14 go unvalidated. Search for references.

10. **Skipping frontend analysis when the PR touches backend (and vice versa).** A change in the API serializer can break the contract with the frontend. A component change can assume a field the backend doesn't send. Always verify both sides when the project is full-stack.

11. **Checklist too vague.** "Test that the filter works" does not tell the tester which filter, with which values, where, or what to expect. "In the Reports view, select the 'From' filter with date 2024-01-01 and 'To' with 2024-12-31. Verify the table shows only records in that range." is actionable.

12. **Not classifying by severity (mandatory vs recommended).** If all tests are presented with equal weight, the tester doesn't know where to start or what blocks the merge.

## Verification Checklist

- [ ] PRs identified: numbers, titles, authors, branches recorded
- [ ] Comments of each PR read and considered
- [ ] Diff of each PR analyzed: modified, added, deleted files
- [ ] Files classified by category (frontend, backend, infra, dependencies, docs)
- [ ] Modules and affected features identified from file paths
- [ ] Source code of modified files read (not just the diff)
- [ ] Execution flow traced for every significant change (frontend: component→API, backend: request→response)
- [ ] Routes and views identified with paths and URL parameters
- [ ] Testing URLs built (with placeholders where data is missing)
- [ ] Permissions and authorization rules verified in the code
- [ ] Validations and edge cases identified from the code
- [ ] Blast radius assessed (references to modified symbols across the code)
- [ ] Missing information requested from the user (base URL, credentials, IDs, PRs)
- [ ] Checklist generated, organized by module, with navigable links
- [ ] Every item traceable to its origin PR
- [ ] Items classified as 🔴 mandatory or 🟡 recommended with consistent criteria
- [ ] No generic, redundant, or unrelated items
- [ ] No invented data (URLs, permissions, behaviors, test data)
- [ ] Checklist reviewed by the user and adjustments applied
- [ ] Delivery format defined and executed (file, PR comment, or conversation)