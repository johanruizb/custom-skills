# Finding Schema

Structured format for audit findings. Every finding MUST contain all required fields.

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "id", "title", "category", "severity", "priority", "confidence",
    "status", "module", "file", "lines", "description", "evidence",
    "reasoning", "impact", "recommendation", "fix_risk", "tests_needed",
    "dependencies", "source", "detected_by"
  ],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^(PERF|BUG|SEC)-\\d{3,}$",
      "description": "Unique identifier: PERF-001, BUG-003, SEC-002"
    },
    "title": {
      "type": "string",
      "description": "Short descriptive title"
    },
    "category": {
      "type": "string",
      "enum": ["performance", "bugs", "security"]
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low", "info"]
    },
    "priority": {
      "type": "string",
      "enum": ["P0", "P1", "P2", "P3"]
    },
    "confidence": {
      "type": "string",
      "enum": ["confirmed", "probable", "hypothesis"],
      "description": "confirmed=verified in code, probable=strong evidence, hypothesis=needs validation"
    },
    "status": {
      "type": "string",
      "enum": ["open", "fixing", "fixed", "wontfix", "skipped"]
    },
    "module": {
      "type": "string",
      "description": "Module or subsystem name"
    },
    "file": {
      "type": "string",
      "description": "Repo-relative path"
    },
    "lines": {
      "type": "string",
      "description": "Line range, e.g., '42-58'"
    },
    "description": {
      "type": "string",
      "description": "What the issue is"
    },
    "evidence": {
      "type": "string",
      "description": "Exact code snippet showing the problem"
    },
    "reasoning": {
      "type": "string",
      "description": "Why this is a problem"
    },
    "impact": {
      "type": "string",
      "description": "What could go wrong if unfixed"
    },
    "reproduction": {
      "type": "string",
      "description": "Steps to reproduce (when applicable)"
    },
    "recommendation": {
      "type": "string",
      "description": "How to fix it"
    },
    "fix_risk": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "description": "Risk of applying the fix"
    },
    "tests_needed": {
      "type": "string",
      "description": "What tests should validate the fix"
    },
    "dependencies": {
      "type": "array",
      "items": {"type": "string"},
      "description": "IDs of findings that must be fixed first"
    },
    "source": {
      "type": "string",
      "description": "Technical reference / doc / CVE (when applicable)"
    },
    "detected_by": {
      "type": "string",
      "description": "Tool or agent that found it"
    }
  }
}
```

## Example Findings

### Security Example

```json
{
  "id": "SEC-001",
  "title": "SQL injection in user search endpoint",
  "category": "security",
  "severity": "critical",
  "priority": "P0",
  "confidence": "confirmed",
  "status": "open",
  "module": "user-service",
  "file": "src/services/userService.js",
  "lines": "34-38",
  "description": "User-supplied search input is concatenated directly into a SQL query string, allowing SQL injection.",
  "evidence": "const query = `SELECT * FROM users WHERE name LIKE '%${req.query.q}%'`;\ndb.execute(query);",
  "reasoning": "The req.query.q parameter comes directly from user input without sanitization or parameterization. An attacker can inject arbitrary SQL by sending q='; DROP TABLE users;--",
  "impact": "Full database compromise: data exfiltration, data modification, data deletion, potential RCE depending on DB configuration.",
  "reproduction": "Send GET /api/users?q=' OR '1'='1' -- to see all users. Send q='; DROP TABLE users;-- to delete the table.",
  "recommendation": "Use parameterized queries: const query = 'SELECT * FROM users WHERE name LIKE ?'; db.execute(query, [`%${req.query.q}%`]);",
  "fix_risk": "low",
  "tests_needed": "Integration test: search with special characters ('; DROP TABLE --). Verify no SQL injection. Add fuzzing test with SQL injection payloads.",
  "dependencies": [],
  "source": "OWASP Top 10 A03:2021 — Injection; https://owasp.org/Top10/A03_2021-Injection/",
  "detected_by": "security-subagent + global grep for string interpolation in SQL"
}
```

### Performance Example

```json
{
  "id": "PERF-001",
  "title": "N+1 query pattern in order list endpoint",
  "category": "performance",
  "severity": "high",
  "priority": "P1",
  "confidence": "confirmed",
  "status": "open",
  "module": "order-service",
  "file": "src/controllers/orderController.ts",
  "lines": "22-35",
  "description": "For each order in the list, a separate query fetches the customer details, causing N+1 queries where N = number of orders.",
  "evidence": "const orders = await Order.findAll({ limit: 100 });\nfor (const order of orders) {\n  order.customer = await Customer.findById(order.customerId);\n}",
  "reasoning": "This executes 1 query for orders + 100 queries for customers = 101 queries. With 100 orders this is already slow; at scale it becomes a major bottleneck.",
  "impact": "API response time grows linearly with order count. At 100 orders: ~1-2s. At 1000 orders: ~10-20s. Database connection pool exhaustion under concurrent load.",
  "recommendation": "Use eager loading / JOIN: const orders = await Order.findAll({ include: Customer, limit: 100 }); or batch fetch: fetch all customerIds in one query.",
  "fix_risk": "low",
  "tests_needed": "Performance test: measure response time with 100 and 1000 orders. Verify single query via query count assertion.",
  "dependencies": [],
  "source": "Sequelize ORM eager loading docs; https://sequelize.org/docs/v6/advanced-associations/eager-loading/",
  "detected_by": "performance-subagent"
}
```

### Bug Example

```json
{
  "id": "BUG-001",
  "title": "Off-by-one error in pagination limit",
  "category": "bugs",
  "severity": "medium",
  "priority": "P2",
  "confidence": "confirmed",
  "status": "open",
  "module": "pagination",
  "file": "src/utils/pagination.py",
  "lines": "15-18",
  "description": "The pagination slice uses range(page * size, page * size + size - 1), which returns size-1 items instead of size items.",
  "evidence": "def get_page(items, page, size):\n    start = page * size\n    return items[start:start + size - 1]",
  "reasoning": "Python slicing is already exclusive on the end index. items[start:start + size] returns `size` items. The -1 causes the last item of each page to be dropped.",
  "impact": "Every page of results shows one fewer item than expected. Users may think there are fewer results than actually exist. Can cause empty last pages.",
  "reproduction": "get_page([1,2,3,4,5,6], page=0, size=5) returns [1,2,3,4] instead of [1,2,3,4,5].",
  "recommendation": "Remove the -1: return items[start:start + size]",
  "fix_risk": "low",
  "tests_needed": "Unit test: verify get_page returns exactly `size` items. Test with size=1, size=5, and size larger than total items.",
  "dependencies": [],
  "source": "",
  "detected_by": "bugs-subagent"
}
```

## Severity Guidelines

| Severity | Criteria |
|---|---|
| critical | Exploitable vulnerability, data loss, or system crash. Fix immediately. |
| high | Significant impact on security, correctness, or performance. Fix soon. |
| medium | Moderate impact. May cause issues under specific conditions. |
| low | Minor impact. Quality issue or edge case. |
| info | Best practice or code quality suggestion. No direct impact. |

## Confidence Guidelines

| Confidence | Criteria |
|---|---|
| confirmed | Issue verified in actual code with clear evidence. No ambiguity. |
| probable | Strong evidence suggests the issue exists, but may need confirmation of runtime behavior or configuration. |
| hypothesis | Pattern matches a known issue, but context may make it non-exploitable or irrelevant. Needs validation before fixing. |

## Priority Guidelines

| Priority | Criteria |
|---|---|
| P0 | Fix now. Blocks release, causes data loss, or is actively exploitable. |
| P1 | Fix soon. Significant risk, should be in next sprint. |
| P2 | Fix when convenient. Moderate risk, schedule for backlog. |
| P3 | Optional improvement. Nice to have, no urgency. |

## Fix Risk Guidelines

| Risk | Criteria |
|---|---|
| low | Isolated change, clear fix, minimal blast radius, tests can verify. |
| medium | Touches shared code, may affect other callers, needs careful testing. |
| high | Core logic change, affects multiple modules, may change behavior expected by other parts. |