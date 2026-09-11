# Final Summary Report Template

Use this template for Phase 5. Fill in every section. If a section has zero items, write "None" — do not omit the section.

---

## Documentation Report: [Project Name]

**Date:** YYYY-MM-DD
**Mode:** [Incremental | Full Regeneration]
**Working directory:** [absolute path]

### Summary

- **Files analyzed:** N
- **Files modified:** N
- **Files excluded:** N
- **Documentation blocks created:** N
- **Documentation blocks updated:** N
- **Comments removed:** N
- **Critical comments preserved:** N

### Files Modified

| File | Language | Changes |
|------|----------|---------|
| `src/auth/login.ts` | TypeScript | 3 functions documented, 1 stale comment updated |
| `src/models/user.py` | Python | 2 class docstrings added, 1 redundant comment removed |
| ... | ... | ... |

### Files Excluded

| File/Directory | Reason |
|----------------|--------|
| `node_modules/` | Third-party dependencies |
| `src/generated/api.ts` | Code-generated file (header: "DO NOT EDIT") |
| `migrations/` | Database migrations, auto-generated |
| ... | ... |

### Critical Comments Preserved

| File | Line | Comment (summary) | Why preserved |
|------|------|--------------------|---------------|
| `src/api/client.ts:42` | Race condition warning | Documents non-obvious concurrency constraint |
| `src/auth/session.py:88` | "We tried JWT, reverted because X" | Historical design decision |
| ... | ... | ... |

### Validation Results

| Tool | Status | Notes |
|------|--------|-------|
| ESLint | PASSED | 0 new warnings |
| TypeScript compiler | PASSED | No type errors |
| Prettier | PASSED | All files formatted |
| pytest | SKIPPED | No test suite found |
| mypy | NOT AVAILABLE | mypy not installed |
| ... | ... | ... |

### Errors and Warnings

- [Any issues introduced or found. "None" if clean.]

### Recommendations

- [Follow-up suggestions, e.g., "Module X has no tests", "Y has complex logic that would benefit from a design doc", "Consider adding a CONTRIBUTING.md with documentation conventions"]

### Git Diff Stats

```
[output of `git diff --stat` if git is available]
```