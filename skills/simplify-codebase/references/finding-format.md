# Finding Format

Every finding from Phase 2 (Deep Analysis) must follow this structured format. This ensures consistency, enables deduplication across subagents, and makes the simplification plan traceable.

## Required Fields

```
ID:              Unique identifier (SIMPL-001, SIMPL-002, ...)
title:           Short descriptive title
category:        duplication | abstraction | redundant-responsibility | redundant-dependency | complex-flow | dead-code | inconsistency
severity:        high | medium | low
confidence:      confirmed | probable | hypothesis
risk:            SAFE | CAREFUL | RISKY
impact:          HIGH | MEDIUM | LOW
module:          Module/subsystem name
files:           List of affected files (with line ranges)
description:     What the issue is (factual, no assumptions)
evidence:        Exact code snippets showing the problem (file:line)
reasoning:       Why this is accidental complexity (not intentional design)
proposal:        What change would simplify it (concrete, minimal)
proposal_risk:    Why the risk level was assigned
validation:      Which tests/linters to run after the change
dependencies:    IDs of findings that must be addressed first (empty if none)
```

## Field Guidelines

### ID
Sequential, prefixed with SIMPL-. Never reuse IDs from reverted findings.

### category
- **duplication**: Same logic implemented multiple times.
- **abstraction**: Unnecessary wrapper, interface, or layer.
- **redundant-responsibility**: Multiple modules doing the same job.
- **redundant-dependency**: Unused or duplicated dependency.
- **complex-flow**: Overly complex call chain, conditional, or state machine.
- **dead-code**: Code with zero references (verified).
- **inconsistency**: Same operation done differently across modules.

### severity
- **high**: Significantly increases complexity or maintenance burden.
- **medium**: Moderate impact on complexity.
- **low**: Minor cleanup (unused imports, commented code).

### confidence
- **confirmed**: Verified by reading the code and searching all reference types.
- **probable**: Strong evidence but some reference types couldn't be fully verified.
- **hypothesis**: Looks like a problem but needs further investigation.

### risk
- **SAFE**: Proven not to affect behavior (dead code with zero references, exact duplicates where one is never called, unused imports).
- **CAREFUL**: Improves without changing semantics (consolidating duplicates, removing pass-throughs, simplifying conditionals). Needs test verification.
- **RISKY**: May change behavior or break contracts (removing code with uncertain references, changing public APIs, restructuring modules). Needs explicit user confirmation.

### impact
- **HIGH**: Reduces complexity across multiple files/modules.
- **MEDIUM**: Improves one module or removes moderate duplication.
- **LOW**: Minor cleanup with limited scope.

## Example Finding

```
ID:              SIMPL-003
title:           Duplicated date formatting in two serializer modules
category:        duplication
severity:        medium
confidence:      confirmed
risk:            CAREFUL
impact:          MEDIUM
module:          reports
files:           backend/reports/serializers.py:45-52, backend/dashboard/serializers.py:78-85
description:     Both serializer modules contain an identical function that formats ISO dates to DD/MM/YYYY. The logic is 8 lines, 100% identical.
evidence:        
                  backend/reports/serializers.py:45-52:
                  ```python
                  def format_date(iso_str):
                      dt = datetime.fromisoformat(iso_str)
                      return dt.strftime('%d/%m/%Y')
                  ```
                  
                  backend/dashboard/serializers.py:78-85:
                  ```python
                  def format_iso_to_display(iso_str):
                      dt = datetime.fromisoformat(iso_str)
                      return dt.strftime('%d/%m/%Y')
                  ```
reasoning:       Two identical implementations of date formatting. Changes to one won't propagate to the other, risking inconsistency.
proposal:        Move to a shared utility module (e.g., utils/dates.py) and import in both serializers. Rename both call sites to use the shared function.
proposal_risk:   CAREFUL — both functions are called within their respective serializers. Need to update all call sites and verify serializers still produce the same output.
validation:      Run serializer tests for both reports and dashboard modules. Run full test suite after change.
dependencies:    None
```

## Consolidation Rules

When consolidating findings from multiple subagents:
1. **Deduplicate**: Same issue in same location = one finding. Keep the one with the most evidence.
2. **Group**: Related findings that share a root cause should be grouped (note the relationship in `dependencies`).
3. **Verify**: Re-read the referenced code to confirm it still matches (files may have changed).
4. **Resolve contradictions**: If one subagent says "dead code" and another says "used dynamically", the one with evidence of dynamic usage wins. Always defer to the evidence.
5. **Rank**: Order by priority (SAFE+HIGH first, RISKY+LOW last).