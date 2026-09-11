# Simplification Plan Template

Use this template to present the prioritized plan to the user in Phase 4.

---

## Codebase Simplification Plan

**Project:** [project name]
**Date:** [date]
**Modules analyzed:** [count]
**Total findings:** [count]
**Breakdown by category:** duplication: X, abstraction: X, dead-code: X, inconsistency: X, complex-flow: X, redundant-dependency: X, redundant-responsibility: X

---

### Priority 1 — SAFE + HIGH Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| SIMPL-001 | [title] | [category] | [file:lines] | [1-sentence description] | [test command] |
| SIMPL-002 | [title] | [category] | [file:lines] | [1-sentence description] | [test command] |

### Priority 2 — SAFE + MEDIUM Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Priority 3 — CAREFUL + HIGH Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Priority 4 — CAREFUL + MEDIUM Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Priority 5 — SAFE + LOW Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Priority 6 — CAREFUL + LOW Impact

| ID | Title | Category | Files | Change | Validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Priority 7 — RISKY (Requires Explicit Confirmation)

| ID | Title | Category | Files | Change | Risk Description | Validation |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | [why it's risky] | [test command] |

---

### Dependency Order

Some changes must be applied before others:
- SIMPL-001 before SIMPL-005 (SIMPL-005 depends on the utility created in SIMPL-001)
- ...

### Summary

- **SAFE changes (can auto-apply):** X items, estimated [trivial/small] effort
- **CAREFUL changes (need test verification):** X items, estimated [small/medium] effort
- **RISKY changes (need explicit confirmation):** X items, estimated [medium/large] effort

### Recommended Approach

1. Apply all SAFE + HIGH first as one batch. Run lint + build + tests.
2. Apply SAFE + MEDIUM next. Run lint + build + tests.
3. Apply CAREFUL changes one file at a time. Run tests after each file.
4. Present RISKY changes individually for user decision.

---

**Confirmation needed:** Which priorities would you like me to apply? You can choose:
- All SAFE priorities (1, 2, 5)
- All SAFE + specific CAREFUL items
- Individual items by ID
- All items (including RISKY, which I'll present one by one)