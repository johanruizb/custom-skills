# Canonical User Questions

Every `user_ask` call in this skill uses one entry from this catalog. Copy the question text, header, options, order, selection mode, and default exactly. `value` is the state representation; `label` and `description` are the UI. Never invent, merge, reorder, or omit options for a decision, unless an entry's **Condition** says otherwise.

## Protocol

1. **Complete call.** For option-based entries, pass `question`, `header`, `options`, and `multiple`; for free-text entries, pass the exact question and use the free-text affordance. Never call the ask tool with no arguments or only a prompt.
2. **One decision per question.** A question carries one setting; an option changes one setting.
3. **Fixed order.** Ask setup questions in the order below, `plan_confirmation` after presenting the plan, and `fix_selection` after presenting the report. Use `fix_blocked` when a preflight blocker occurs and `risky_confirmation` before fixing RISKY findings. Batch independent setup questions in one call when the harness supports it.
4. **Canonical values.** Record `value`, not `label`. Labels may be translated directly; values, order, and defaults stay fixed.
5. **Catalog follow-ups.** When a choice needs detail, ask its follow-up from this catalog; never improvise a new question.
6. **Resume.** Reuse answers recorded in state. Ask only unanswered questions, or questions invalidated by changed inputs.
7. **Free text.** For entries marked free text, use the native free-text affordance or present the exact prompt in conversation. If the structured tool requires at least one option, pass the single option `Enter value` with description `Type the value in the custom answer`; do not add decision options. Re-ask on invalid input.

## Setup questions (Phase 3)

### `focus_areas`

- **Header**: `Focus areas`
- **Question**: `Which focus areas should the audit cover?`
- **Selection**: multiple
- **Default**: all four values
- **State**: `config.areas` (array of values)

| Value | Label | Description |
|---|---|---|
| `bugs` | Bugs | Correctness defects, crashes, and broken failure paths. |
| `security` | Security | Vulnerabilities, exposed secrets, and unsafe input handling. |
| `performance` | Performance | Hotspots, unnecessary work, and resource leaks. |
| `simplification` | Simplification | Duplication, dead code, and unnecessary abstractions. |

### `scope`

- **Header**: `Scope`
- **Question**: `What scope should the audit cover?`
- **Selection**: single
- **Default**: `entire-repo`
- **State**: `config.scope_mode` (canonical method); `config.scope` holds the paths/modules when not `entire-repo`

| Value | Label | Description |
|---|---|---|
| `entire-repo` | Entire repository (Recommended) | Audit every module in the repository. |
| `folders` | Specific folders | Limit the audit to folder paths you provide. |
| `modules` | Specific modules | Limit the audit to modules from the project map. |

Follow-up: `scope_folders` for `folders`; `scope_modules` for `modules`.

### `scope_folders`

- **Header**: `Folder paths`
- **Question**: `Which folder paths should the audit cover? Enter comma-separated paths relative to the repository root.`
- **Selection**: free text
- **Validation**: every path must exist; reject invalid paths and re-ask this exact question.
- **State**: `config.scope` (comma-separated paths); `config.scope_mode=folders`

### `scope_modules`

- **Header**: `Modules`
- **Question**: `Which modules should the audit cover?`
- **Selection**: multiple
- **Options**: one per `project_map.modules[].name`, sorted by name; label is the module name, description is its path. Do not invent options.
- **Validation**: every value must exist in `project_map.modules`; reject unknown values and re-ask.
- **State**: `config.scope` (comma-separated module names); `config.scope_mode=modules`

### `exclusions`

- **Header**: `Exclusions`
- **Question**: `Should any paths be excluded beyond the automatic exclusions?`
- **Selection**: single
- **Default**: `none`
- **State**: `config.exclusions` (array; empty for `none`)

| Value | Label | Description |
|---|---|---|
| `none` | No extra exclusions (Recommended) | Use the auto-detected exclusion list only. |
| `add` | Add exclusions | Provide paths to exclude from the audit. |

Follow-up: `exclusion_paths` for `add`.

### `exclusion_paths`

- **Header**: `Exclusion paths`
- **Question**: `Which paths should be excluded? Enter comma-separated paths or globs relative to the repository root.`
- **Selection**: free text
- **State**: `config.exclusions` (array)

### `depth`

- **Header**: `Depth`
- **Question**: `How deep should the audit go?`
- **Selection**: single
- **Default**: `standard`
- **State**: `config.depth`

| Value | Label | Description |
|---|---|---|
| `standard` | Standard (Recommended) | Module-by-module deep read. |
| `quick` | Quick | Surface patterns and fast checks. |
| `exhaustive` | Exhaustive | Every file plus dependency analysis. |

### `html_report`

- **Header**: `HTML report`
- **Question**: `Do you want an HTML report?`
- **Selection**: single
- **Default**: `no`
- **Condition**: ask only when `file_write` is available; otherwise record `no` and log the limitation.
- **State**: `config.html_report` (boolean: `yes` → true, `no` → false)

| Value | Label | Description |
|---|---|---|
| `no` | No HTML report (Recommended) | Return the report inline. |
| `yes` | Generate HTML report | Write a standalone HTML file. |

### `execution_mode`

- **Header**: `Execution mode`
- **Question**: `How should findings be handled after the audit?`
- **Selection**: single
- **Default**: `audit-select`
- **State**: `config.mode`

| Value | Label | Description |
|---|---|---|
| `audit-select` | Choose fixes after report (Recommended) | Report, then select fixes interactively. |
| `audit-only` | Audit only | Report findings; make no changes. |
| `audit-auto` | Auto-fix safe findings | Report, then fix confirmed low-risk findings. |

### `subagents`

- **Header**: `Subagents`
- **Question**: `Should the audit use subagents when the harness supports them?`
- **Selection**: single
- **Default**: `yes`
- **Condition**: ask only when `subagent_spawn` is available; otherwise record `no` and log the limitation.
- **State**: `config.use_subagents` (boolean: `yes` → true, `no` → false)

| Value | Label | Description |
|---|---|---|
| `yes` | Use subagents (Recommended) | Parallelize analysis when available. |
| `no` | Run sequentially | Keep all analysis in the main agent. |

### `isolation`

- **Header**: `Fix isolation`
- **Question**: `How should authorized fixes be isolated?`
- **Selection**: single
- **Default**: `worktree`
- **Condition**: record `worktree` without asking when git worktree is available and the primary tree is clean. Ask only when that default is unavailable or the user requests a change. When `execution_mode=audit-only`, record `none` without asking. When git or `cmd_exec` is unavailable, omit `worktree` and record the omission reason.
- **State**: `isolation.strategy`: `worktree` → `worktree`, `in-place` → `in-place`, `audit-only` → `none`. If no fixes are selected later, set `none`.

| Value | Label | Description |
|---|---|---|
| `worktree` | Dedicated worktree (Recommended) | Create a new branch and worktree from the audited commit; requires a clean primary tree. |
| `in-place` | Edit in place | Apply fixes in the current checkout. |
| `audit-only` | Audit only | Make no changes. |

## Preflight and fallback

### `fix_blocked`

- **Header**: `Fix preflight`
- **Question**: `Fix isolation cannot proceed: <reason>. How should the run proceed?`
- **Fill**: replace `<reason>` with the concrete blocker (dirty tree, missing untracked/ignored files, worktree creation failure, unwritable worktree parent).
- **Selection**: single
- **Default**: none
- **State**: `answers.fix_blocked`

| Value | Label | Description |
|---|---|---|
| `resolve` | I will resolve it (Recommended) | Pause while I clean the tree, provide missing files, or provide a writable worktree location; then retry. |
| `in_place` | Edit in place | Apply fixes in the current checkout. |
| `audit_only` | Audit only | Make no changes. |

On `resolve`: wait for the user, then re-run the worktree preflight. On `in_place`: set `isolation.strategy=in-place`. On `audit_only`: set `isolation.strategy=none`.

## Plan confirmation

### `plan_confirmation`

- **Header**: `Confirm plan`
- **Question**: `Proceed with this audit plan?`
- **Selection**: single
- **Default**: none; the audit starts only on `proceed`
- **State**: `answers.plan_confirmation`

| Value | Label | Description | Next |
|---|---|---|---|
| `proceed` | Proceed as planned (Recommended) | Start the audit with the recorded configuration. | Phase 4 |
| `adjust_scope` | Adjust scope | Change scope or exclusions, then review the plan again. | Re-ask `scope` and `exclusions` |
| `adjust_areas` | Adjust focus areas | Change focus areas or depth, then review the plan again. | Re-ask `focus_areas` and `depth` |
| `adjust_mode` | Adjust execution | Change execution mode, report, or subagents, then review the plan again. | Re-ask `execution_mode`, `html_report`, and `subagents`; reconcile `isolation` |
| `adjust_isolation` | Adjust isolation | Change how fixes are isolated, then review the plan again. | Re-ask `isolation` (keep `none` when mode is `audit-only`) |
| `cancel` | Cancel audit | Stop without auditing or changing code. | End run |

After any `adjust_*` answer: re-ask the listed questions, update the plan, and ask `plan_confirmation` again. Reconcile `isolation` after `adjust_mode`: when mode becomes `audit-only`, set `none`; when mode becomes fix-capable and isolation is `none`, record the default `worktree` or ask `isolation` if the default is unavailable.

## Fix selection

### `fix_selection`

- **Header**: `Fix selection`
- **Question**: `Which findings should be fixed?`
- **Selection**: single
- **Default**: none
- **Condition**: ask only when `config.mode=audit-select`; for `audit-only` record `audit_only`, for `audit-auto` record `all_safe`.
- **State**: `answers.fix_selection_method`

| Value | Label | Description | Follow-up |
|---|---|---|---|
| `all_safe` | All safe fixes (Recommended) | Confirmed findings with `fix_risk=low` (SAFE). | None |
| `critical_high` | Critical and high severity | Every finding at critical or high severity. | None |
| `confirmed` | All confirmed findings | Every finding whose evidence is confirmed. | None |
| `by_id` | Choose by finding ID | Provide the finding IDs to fix. | `include_finding_ids` |
| `by_category` | Choose by category | Fix every finding in selected categories. | `fix_category` |
| `by_module` | Choose by module | Fix every finding in selected modules. | `fix_module` |
| `all_except` | All except specific IDs | Fix everything except the IDs you exclude. | `exclude_finding_ids` |
| `audit_only` | Audit only | Make no changes. | None |

Any selection that resolves to a RISKY finding requires `risky_confirmation` before Phase 8; if `safe_only` leaves no findings, ask `fix_selection` again.

### `risky_confirmation`

- **Header**: `Risky fixes`
- **Question**: `These findings are RISKY: <IDs>. Include them in the fix run?`
- **Fill**: replace `<IDs>` with the comma-separated RISKY finding IDs.
- **Selection**: single
- **Default**: none
- **State**: `answers.risky_confirmation`

| Value | Label | Description |
|---|---|---|
| `safe_only` | Safe and careful only (Recommended) | Drop RISKY findings and fix the rest. |
| `include_risky` | Include risky fixes | Apply the listed RISKY findings too. |
| `cancel` | Cancel fixes | Make no changes. |

If `safe_only` leaves no findings, ask `fix_selection` again. `cancel` ends the fix run; the audit report remains.

### `include_finding_ids`

- **Header**: `Finding IDs`
- **Question**: `Which finding IDs should be fixed? Enter comma-separated IDs from the report.`
- **Selection**: free text
- **Validation**: every ID must exist in `findings`; reject unknown IDs and re-ask this exact question.
- **State**: `answers.fix_selection_detail` (array)

### `exclude_finding_ids`

- **Header**: `Exclude IDs`
- **Question**: `Which finding IDs should be excluded? Enter comma-separated IDs from the report.`
- **Selection**: free text
- **Validation**: every ID must exist in `findings`; reject unknown IDs and re-ask this exact question.
- **State**: `answers.fix_selection_detail` (array)

### `fix_category`

- **Header**: `Category`
- **Question**: `Which categories should be fixed?`
- **Selection**: multiple
- **State**: `answers.fix_selection_detail` (array)

| Value | Label | Description |
|---|---|---|
| `performance` | Performance | Findings in the performance category. |
| `bugs` | Bugs | Findings in the bugs category. |
| `security` | Security | Findings in the security category. |
| `simplification` | Simplification | Findings in the simplification category. |

### `fix_module`

- **Header**: `Module`
- **Question**: `Which modules should be fixed?`
- **Selection**: multiple
- **Options**: one per `project_map.modules[].name`, sorted by name; label is the module name, description is its path. Do not invent options.
- **Validation**: every value must exist in `project_map.modules`; reject unknown values and re-ask.
- **State**: `answers.fix_selection_detail` (array)
