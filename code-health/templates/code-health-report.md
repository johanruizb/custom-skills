# Findings Report Template

Use this template to deliver the Phase 7 report for an audit or cleanup run. Fill every section. A section with zero items says "None".

---

## Code Health Report: [project name]

**Date:** YYYY-MM-DD
**Focus areas:** [bugs | security | performance | simplification, as configured]
**Depth:** [quick | standard | exhaustive]
**Execution mode:** [audit-only | audit-select | audit-auto]

### Summary

- Technologies detected: [languages, frameworks, exact versions]
- Files/modules analyzed: N (omitted: N, with reason)
- Findings total: N

| Category | critical | high | medium | low | info |
|---|---|---|---|---|---|
| performance |  |  |  |  |  |
| bugs |  |  |  |  |  |
| security |  |  |  |  |  |
| simplification (duplication / abstraction / dead-code / inconsistency / complex-flow / dependencies) |  |  |  |  |  |

### Top Risks

1. [finding ID + one-sentence why it is first]

### Findings

Grouped by category, in priority order. Each finding carries the full `references/finding-schema.md` format: file:line evidence, code snippet, reasoning, impact, recommendation, fix risk, tests needed, dependencies. For simplification work include the complexity hotspots (modules with the most findings, deepest call chains, most duplication).

### Tools

- Used: [tool name: what it reported]
- Unavailable: [tool name: impact on the audit]

### Limitations

- Missing tools, unverified hypotheses, areas not covered.

### Recommended Resolution Order

1. [finding IDs in dependency-and-priority order]

---

(For audit-only runs the report ends here. For fix runs, add the sections below after the user picks findings.)

## Fixes Applied

| ID | Title | Files | Change | Validation |
|---|---|---|---|---|
| [ID] | [title] | [paths] | [1-2 sentences] | passed / failed / reverted |

### Skipped or Reverted

| ID | Reason |
|---|---|
| [ID] | [why] |

### Validation

| Check | Command | Result | Notes |
|---|---|---|---|
| Test suite | [command] | passed (X ok, Y failed) / not_run |  |
| Linter | [command] | passed / failed / not_run |  |
| Type checker | [command] | passed / failed / not_run |  |
| Build | [command] | passed / failed / not_run |  |

Checks that could not run: [name, reason, what the user should run manually].

### Metrics (simplification runs)

| Metric | Count |
|---|---|
| Duplications eliminated | N |
| Dead code removed (lines / files) | N |
| Unnecessary abstractions removed | N |
| Inconsistent patterns unified | N |
| Files affected | N |
| Net lines (removed / added) | -N / +N |

### Opportunities Pending

1. [finding ID: why pending, what unblocks it]
2. [recommended next steps, e.g., deeper analysis with other skills]