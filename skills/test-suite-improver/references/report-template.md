# Report Template

Template for the Phase 10 final report. Use this structure for both the inline summary and the generated Markdown/HTML report.

---

## Markdown Template

```markdown
# Test Suite Improvement Report

**Project:** [project name from repo root]
**Date:** [YYYY-MM-DD]
**Work mode:** [Mode 1 — Improve | Mode 2 — Rebuild | Mode 3 — Analysis only]

---

## 1. Technologies Detected

| Category | Technology | Version |
|---|---|---|
| Language | [language] | [version] |
| Framework | [framework] | [version] |
| Test runner | [runner] | [version] |
| Assertion lib | [library] | [version] |
| Mocking lib | [library] | [version] |
| Coverage tool | [tool] | [version] |
| CI | [system] | — |

## 2. Initial State

| Metric | Value |
|---|---|
| Total tests | [N] |
| Passed | [N] |
| Failed | [N] |
| Skipped | [N] |
| Errors | [N] |
| Duration | [Xs] |
| Coverage (line) | [X%] |
| Coverage (branch) | [X%] |
| Blockers | [none / description] |

### Test infrastructure detected
- Fixtures: [yes/no — details]
- Factories: [yes/no — details]
- Mocks: [yes/no — details]
- Test DB: [yes/no — details]
- Helpers: [yes/no — details]

## 3. Work Mode Selected

[Mode 1 / 2 / 3 — brief justification of why this mode was chosen]

## 4. Test Suite Changes

### Tests Created ([N])
| File | Test name | Behavior tested | Type |
|---|---|---|---|
| `tests/test_foo.py` | `test_bar` | [behavior] | [unit/integration/e2e] |
| ... | ... | ... | ... |

### Tests Fixed ([N])
| File | Test name | Issue | Fix |
|---|---|---|---|
| `tests/test_baz.py` | `test_qux` | [smell] | [what changed] |
| ... | ... | ... | ... |

### Tests Removed ([N])
| File | Test name | Reason | Evidence |
|---|---|---|---|
| `tests/test_old.py` | `test_deleted_feature` | Obsolete | [line X: imports removed function] |
| `tests/test_dup.py` | `test_copy` | Duplicate of `test_create_user` | [identical setup and assertions] |
| ... | ... | ... | ... |

### Tests Kept ([N])
[N] tests retained without changes. All passed validation.

## 5. Functionality Covered

| Functionality | Tests | Risk level | Status |
|---|---|---|---|
| User authentication | [test names] | Critical | Covered |
| Email validation | [test names] | High | Covered |
| Payment processing | [test names] | Critical | Partial — missing retry path |
| ... | ... | ... | ... |

## 6. Risks Without Coverage

| Risk | Impact | Recommendation |
|---|---|---|
| [untested behavior] | [critical/high/medium/low] | [recommended test] |
| ... | ... | ... |

## 7. Validation Results

| Check | Result | Details |
|---|---|---|
| New tests pass | [passed/failed/not_run] | [N passed, N failed] |
| Full suite passes | [passed/failed/not_run] | [N passed, N failed, N skipped] |
| Mutation verification | [passed/failed/not_run] | [N/N tests verified to fail on code break] |
| Linter | [passed/failed/not_run] | [output summary] |
| Type checker | [passed/failed/not_run] | [output summary] |
| Build/compile | [passed/failed/not_run] | [output summary] |
| App startup | [passed/failed/not_run] | [output summary] |

### Coverage Change

| Module | Before (line) | After (line) | Before (branch) | After (branch) |
|---|---|---|---|---|
| `services/user.py` | [X%] | [Y%] | [X%] | [Y%] |
| `api/endpoints.py` | [X%] | [Y%] | [X%] | [Y%] |
| **Overall** | [X%] | [Y%] | [X%] | [Y%] |

## 8. Pending Issues and Limitations

- [Missing tools that affected the run — e.g., "coverage tool not installed, coverage numbers are estimates"]
- [Tests that couldn't run — e.g., "integration tests require PostgreSQL, which is not available in this environment"]
- [Unverified hypotheses — e.g., "test_foo is suspected tautological but couldn't verify because the tested function couldn't be located"]
- [Flaky tests detected — e.g., "test_async_poll failed once on retry, possible race condition"]

## 9. Future Recommendations

1. [Recommendation — e.g., "Add a pre-commit hook to run the test suite on push"]
2. [Recommendation — e.g., "Separate integration tests into a dedicated suite that runs in CI only"]
3. [Recommendation — e.g., "Adopt factory_boy for test data generation to reduce fixture duplication"]
4. [Recommendation — e.g., "Set up mutation testing (mutmut / Stryker) to measure test effectiveness"]
5. [Recommendation — e.g., "Review the test suite quarterly — remove obsolete tests, add tests for new features"]

---

## Sources Consulted

- [Source 1 — URL]
- [Source 2 — URL]
- ...
```

---

## HTML Report Generation

When `file_write` and `cmd_exec` are available, generate an HTML report:

```python
#!/usr/bin/env python3
"""Generate HTML test suite report from Markdown."""
import sys
from pathlib import Path

def markdown_to_html(md_path, output_path):
    content = Path(md_path).read_text()
    # Minimal markdown to HTML conversion
    # (use a library like `markdown` if available, or basic regex conversion)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test Suite Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f4f4f4; }}
  h1, h2, h3 {{ color: #333; }}
  code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
  pre {{ background: #f8f8f8; padding: 1em; border-radius: 5px; overflow-x: auto; }}
</style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>"""
    Path(output_path).write_text(html)
    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    markdown_to_html(sys.argv[1], sys.argv[2])
```

Run with: `python generate_report.py report.md /tmp/test-suite-report.html`
Open with: `xdg-open /tmp/test-suite-report.html` (Linux) or `open /tmp/test-suite-report.html` (macOS)