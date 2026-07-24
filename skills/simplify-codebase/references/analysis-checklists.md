# Analysis Checklists

Checklists for each category of accidental complexity. Use these during Phase 2 (Deep Analysis) to systematically inspect each module.

## 1. Code Duplication Checklist

### Function/Method Level
- [ ] Are there functions with the same name in different modules that do the same thing?
- [ ] Are there functions with different names that do the same thing? (search by behavior, not name)
- [ ] Are there functions that are 80%+ identical (same logic, minor variation in params/names)?
- [ ] Are there utility functions reimplementing standard library / framework functionality?
- [ ] Are there multiple implementations of the same algorithm (e.g., two date parsers, two formatters, two validators)?

### Block Level
- [ ] Are there copy-pasted blocks (5+ lines) that appear in multiple files?
- [ ] Are there conditional blocks that repeat the same pattern with different variables?
- [ ] Are there try/except blocks that handle the same error the same way in multiple places?
- [ ] Are there API call patterns (fetch/axios/requests) duplicated across modules?

### Module Level
- [ ] Are there multiple utility files (utils.py, helpers.py, common.py, shared.py) with overlapping content?
- [ ] Are there multiple modules that implement the same domain concept?
- [ ] Are there parallel class hierarchies that could be unified?

### Cross-Project
- [ ] Are there constants defined in multiple places that should be in one config?
- [ ] Are there regex patterns / format strings duplicated across the codebase?
- [ ] Are there error messages / validation messages duplicated?

## 2. Unnecessary Abstractions Checklist

### Wrapper Detection
- [ ] Functions that only call another function (pass-through wrappers)?
- [ ] Classes that only delegate to another class?
- [ ] Manager classes that add no logic beyond delegation?
- [ ] Factory classes/functions that always return the same type?
- [ ] Adapter classes with a single adapter and no variation point?

### Interface Bloat
- [ ] Interfaces/abstract classes with a single implementation?
- [ ] Generic helpers so abstract they require more boilerplate than the direct code?
- [ ] Builder patterns where a simple constructor would do?
- [ ] Strategy patterns where only one strategy is ever used?

### Layer Redundancy
- [ ] Service layers that just call the repository and return?
- [ ] Controller layers that just call the service and return?
- [ ] Multiple serialization layers that transform data without adding information?
- [ ] Configuration loaders that go through multiple intermediate representations?

### Deletion Test
For each suspected abstraction, ask: "If I delete this and inline its body at the call site, does the code become simpler?" If yes, it's unnecessary.

## 3. Redundant Responsibilities Checklist

- [ ] Multiple modules handling the same concern (e.g., auth logic in 3 places)?
- [ ] Overlapping utility modules (utils.py + helpers.py + common.py)?
- [ ] Multiple error-handling patterns (some use try/except, some use .catch, some use Result types)?
- [ ] Multiple logging patterns (some use logger, some use console.log, some use print)?
- [ ] Multiple config-reading patterns (some use env vars directly, some use a config loader, some hardcode)?
- [ ] Multiple HTTP client patterns (some use fetch, some use axios, some use a custom wrapper)?

## 4. Redundant Dependencies Checklist

### External Dependencies
- [ ] Dependencies declared in manifest but never imported? (check package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml)
- [ ] Multiple libraries for the same purpose? (requests + httpx, moment + date-fns, lodash + ramda)
  - NOTE: A migration in progress is a valid reason. Only flag if both are used for the same purpose in production code.
- [ ] Dev dependencies that should be dev-only but are in the main deps?

### Internal Dependencies
- [ ] Internal modules that wrap a single external library call and add no value?
- [ ] Internal modules imported by only one other module (could be inlined)?
- [ ] Circular dependencies between modules?

## 5. Excessively Complex Flows Checklist

### Call Chain Depth
- [ ] Call chains > 4 levels deep where intermediate levels are pass-throughs?
- [ ] Request flows that pass through unnecessary middleware/layers?
- [ ] Data transformations that go through unnecessary intermediate formats?

### Conditional Complexity
- [ ] Nested conditionals > 3 levels deep?
- [ ] Functions with > 10 branches (if/elif/else/switch)?
- [ ] Boolean expressions with > 4 terms that could be simplified?
- [ ] God functions that handle too many cases (should be split by responsibility)?

### State Complexity
- [ ] State machines that could be simple conditionals?
- [ ] Global mutable state that could be local?
- [ ] State flags that are always set together (should be a single state)?
- [ ] Optional values that are never actually None/undefined?

## 6. Dead or Unused Code Checklist

### Before Flagging — Check ALL Reference Types
1. **Direct imports**: `from module import name`, `import module`
2. **Dynamic imports**: `importlib.import_module()`, `__import__()`
3. **String references**: `getattr(module, 'name')`, settings strings, URL patterns
4. **Django-specific** (if applicable):
   - `INSTALLED_APPS` references
   - URL patterns (`path('', include('app.urls'))`)
   - Serializer `Meta.model = 'app.ModelName'`
   - Signal handlers (`@receiver(post_save, sender='app.Model')`)
   - Management commands (auto-discovered by file name)
   - Template tags registered by module path
   - Middleware classes in settings
   - Auth backends in settings
   - Database routers in settings
5. **React/frontend-specific** (if applicable):
   - Components referenced by string in routes
   - Lazy imports (`React.lazy(() => import('...'))`)
   - Dynamic component names
6. **Config references**: YAML/TOML/JSON/INI files that reference module paths
7. **Test references**: test files that import the code
8. **Build references**: webpack/vite/rollup configs that reference entry points

### Dead Code Categories
- [ ] Functions/methods never called (verified by comprehensive search)
- [ ] Classes never instantiated (verified)
- [ ] Constants/variables never read (verified)
- [ ] Imports not used in the file
- [ ] Commented-out code blocks (> 3 lines)
- [ ] Files not imported/referenced by anything
- [ ] Feature flags that are never enabled
- [ ] Disabled/bypassed code paths (if False: / if 0: / # noqa)

### Confidence Levels
- **confirmed**: Searched all reference types, zero references found. Safe to remove.
- **probable**: Searched most reference types, very likely unused. But some dynamic patterns might have been missed.
- **hypothesis**: Looks unused but couldn't verify all reference types. Do NOT remove without user confirmation.

## 7. Inconsistent Patterns Checklist

### Within the Same Project
- [ ] Same operation done differently across modules (e.g., some use a shared API client, others use raw fetch)?
- [ ] Error handling: some modules use try/except, others use .catch(), others use no handling?
- [ ] Naming: same concept named differently across modules (e.g., `userId` vs `user_id` vs `UserID`)?
- [ ] File organization: some modules have separate views.py/serializers.py, others combine them?
- [ ] Test patterns: some use factories, some use manual setup, some use fixtures?
- [ ] Logging: some use logger.info, others use print, others use console.log?
- [ ] Config access: some use env vars, some use a config object, some hardcode?
- [ ] Response formatting: some endpoints return {data: ...}, others return raw objects?
- [ ] Validation: some use schema validation, some use manual checks, some use framework validators?

### Consistency Rules
- Only flag patterns that are genuinely inconsistent *within the same project*.
- Do NOT flag a pattern just because it differs from your personal preference.
- Do NOT flag a pattern that is consistent but "unconventional" — if the whole project uses it, it's a convention.
- The goal is internal consistency, not adherence to external best practices (unless the user asks for that).

## How to Use These Checklists

1. **Per module**: Go through each checklist for each module during Phase 2.
2. **Evidence required**: Every finding must cite file:line with a code snippet.
3. **No speculation**: If you can't point to specific code, don't raise the finding.
4. **Confidence labeling**: Mark each finding as confirmed / probable / hypothesis.
5. **Cross-module**: After per-module analysis, do a cross-module pass for duplication and inconsistency (these only appear when comparing modules).
6. **Use tools**: `search_files` for content search, `read_file` for reading files, `terminal` for running detection scripts (see `scripts/detect-duplicates.py`).