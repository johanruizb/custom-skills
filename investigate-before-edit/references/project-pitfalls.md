# Project-Specific Pitfalls

> Case-study pitfalls from real investigations. Pitfalls 1-11 are generic and stay in SKILL.md; these assume a Django + DRF + MUI stack and specific implementation details. Treat them as patterns to adapt, not universal rules.

12. **Assuming the execution environment without verification.** When the user reports a runtime behavior (e.g., "I'm getting 403s"), do NOT assume which code path is executing — verify it. Check `git branch`, `git log`, and the actual file contents on disk. The user may be running from a worktree, a different branch, or a stale build. Claims like "you must be running from the old repo" without evidence are frustrating and waste time. Instead: run `git branch` to confirm the branch, check `git log --oneline -3` to see recent commits, and verify the relevant file's content by reading it before making any claim about what code is executing.

13. **Not checking the actual HTTP response before diagnosing a frontend issue.** When the user reports a 404 or 403 in the browser, verify the actual HTTP response with `curl` before assuming the problem is in the frontend code. The backend may be returning a different status code than the user described, or the error may be a data issue (record not found) rather than a permission issue. Always `curl` the endpoint with the same headers (Authorization, Referer) the browser would send.

14. **Assuming the backend is the problem when the frontend shows an error toast/message.** When the user reports "Error al cargar X" or any frontend error toast, the investigation order matters:
    - **First:** Check the browser console for JS errors. A silent JS error (e.g., calling `.get()` on a string, undefined is not a function) can cause SWR to show an error even when the backend returns 200.
    - **Second:** Curl the endpoint directly with the same auth headers to confirm the backend is actually returning an error.
    - **Third:** Trace the frontend fetcher function — verify it uses the correct API utility. In projects with custom API wrappers (e.g., `getProxy()` returning a string vs `makeAPIRequest` using an Axios instance), the fetcher may be calling a method on the wrong object.
    - **Fourth:** Check the SWR key for collisions or stale data.
    - **Only then** investigate the backend view/serializer.

    The most common cause of "Error al cargar X" with a 200 backend response is a bug in the frontend fetcher function, not a backend issue.

15. **Django+DRF middleware ordering.** See `references/django-drf-multitenant-permissions.md` for middleware ordering, DRF authentication timing, and custom permission classes.

16. **Don't invent data from training data — verify from the actual source.** When the user reports a behavior (e.g., "these roles don't exist" or "the data looks wrong"), do NOT assume the data from your training corpus is correct. Your training data may contain plausible-looking data that doesn't exist in the actual database. Always:
    - Query the actual database or API endpoint to verify what data exists.
    - Check `git log` and `git branch` to confirm which code is running.
    - Read the actual file contents on disk, not your memory of what they should contain.
    - If the user says the data is invented, they're right — you invented it. Stop, verify from the actual source, and apologize.
    - Common symptom: claiming a user has certain roles, permissions, or data based on what "makes sense" rather than what the database actually contains. The database is the source of truth, not your training data.

17. **Multi-tenant investigation: always check tenant isolation.** In a multi-tenant app, a bug that appears for one tenant may not appear for another. When investigating:
    - Check if the issue is tenant-specific by testing with a different tenant's data.
    - Verify `_church_context` / `id_church` filters in queries — a record with `id_church=None` (global) won't be found by a query filtering for a specific church.
    - Check if the data exists for the specific tenant, not just globally. A 404 may mean "this record doesn't belong to this tenant" rather than "this record doesn't exist."
    - When migrating data, verify per-tenant: run the migration, then query each tenant's data to confirm it arrived correctly. Don't trust the migration summary alone.
    - Global records (e.g., `positions_per_group` with `id_church=None`) need special handling — they must be replicated to every tenant, not skipped.

18. **Migration verification: don't trust the summary, query the database.** After running a data migration:
    - Query the actual database to verify counts and specific records.
    - Check edge cases: global records, records with null foreign keys, records that already existed before the migration.
    - Run the migration twice to verify idempotency (get_or_create should not create duplicates).
    - Verify that the migration didn't skip records it shouldn't have (e.g., global records with `id_church=None`).
    - Check that the migration updated ALL relevant records, not just the first match per group.

19. **Check for data loss when a CharField is replaced by a FK.** When a migration drops a CharField and adds a FK (`RemoveField` + `AddField`), verify there's a `RunPython` operation BETWEEN them that migrates the data. Without it, all existing values are permanently lost. The `RunPython` must come BEFORE `RemoveField` — the old field is only accessible in the historical model at that point. If the migration has already been applied and the data is lost, the only recovery path is a hardcoded mapping of known values.

20. **Data format mismatch between frontend and backend.** When the frontend shows empty data, "undefined", or renders nothing but the backend returns 200, the most common cause is a mismatch between the data format the backend sends and what the frontend expects. Investigation order:
    - **First:** Curl the endpoint and inspect the raw JSON response structure. Note the top-level keys and nesting.
    - **Second:** Check what the frontend fetcher does with the response — does it access `res.data`? Does it expect `response.modules` or `response.results`?
    - **Third:** Compare the backend response structure with the frontend's expected structure. Common mismatches: backend returns a list but frontend expects `{modules: [...]}`; backend returns `{results: [...]}` but frontend expects a list; backend returns camelCase but frontend expects snake_case (or vice versa).
    - **Fourth:** Check the SWR key and fetcher function. The fetcher may be transforming the data (e.g., `.then(res => res.data)`) and the component may be accessing a property that doesn't exist on the transformed result.
    - **Fifth:** Check if the endpoint changed recently (git log for the view/serializer). A serializer change that renamed a field or changed nesting can silently break the frontend.
    - **Sixth:** Check the browser console for JS errors — a silent JS error (e.g., calling `.get()` on a string, `undefined.reduce()`, `undefined is not a function`) can cause SWR to show an error even when the backend returns 200.
    - Common pattern: backend returns `[{key, label, resources}, ...]` but frontend accesses `catalog.modules` — the fix is to use `catalog` directly, not `catalog.modules`.
    - Common pattern: `getProxy().get(...)` where `getProxy()` returns a string (not an Axios instance); `makeAPIRequest` with wrong argument order; missing `.then(res => res.data)` on Axios response.

21. **Callback that ignores the payload.** When a parent component passes an `onSave` callback to a child form, verify that the callback actually uses the payload it receives. Common anti-pattern: `onSave={() => setSelectedId(null)}` — the callback clears state but never calls the API. The child calls `onSave(payload)` expecting the parent to persist it. Always check: does the parent's `onSave` implementation call the backend API with the payload, or does it just reset UI state? This applies to `onSave`, `onSubmit`, `onDelete`, and any callback that should trigger a side effect.

22. **`is_superuser` not exposed to the frontend.** When the frontend needs to know if a user is a superuser (e.g., to show/hide admin features), verify the login/session serializer includes `is_superuser` in its output. Django's `User.is_superuser` is a model field, but serializers often omit it. Add `is_superuser = serializers.BooleanField()` to the serializer — do NOT use `source="is_superuser"` (DRF rejects this with `KeyError` when the field name matches the source; just use `BooleanField()` without `source`).

23. **Browser debugging is the LAST resort, not the first.** When the user reports a UI bug (e.g., "clicking a group does nothing"), the investigation order MUST be:
    - **First:** Read the relevant source code. The code is the source of truth. The browser shows symptoms, not causes.
    - **Second:** Check git log for recent commits that may have introduced the bug.
    - **Third:** Only if the code logic is correct and the symptom persists, use the browser to verify the runtime state (console, network tab, DOM inspection).
    - **NEVER** spend 40 minutes clicking around the browser when the code is available to read. The user will (rightfully) tell you to stop wasting tokens.
    - **NEVER** restart the Vite dev server as a debugging step — the code on disk is what matters. If the browser shows stale behavior, delete `.vite/` cache and do a hard reload (Ctrl+Shift+R), but only after verifying the code is correct.
    - **NEVER** assume the browser shows the real state of the code. Vite HMR can serve stale modules. The code on disk is the source of truth.
    - **Signal to stop browser debugging:** If you've made 3+ browser navigation/console calls without finding the root cause, STOP. Read the code instead. The root cause is in the code, not in the browser.
    - **Exception:** If the bug is clearly a runtime data issue (e.g., "the API returns 200 but the UI shows nothing"), one browser console call to check the API response is acceptable. Then read the code that processes that response.
    - **User override signal:** If the user expresses frustration about browser debugging (in any wording), STOP IMMEDIATELY. Do not make another browser call. Do not restart Vite. Do not check the console again. Read the code. The user is telling you the root cause is in the code, not the browser. Every browser call after this signal is actively wasting the user's patience and tokens. If you already made browser calls and didn't find the cause, the answer is in the code — read it.
    - **HARD RULE:** After the user signals to stop, you get exactly ONE more action: read the relevant source file. If you don't find the root cause in that one read, you missed something in your earlier code reading. Re-read the file more carefully. Do NOT make another browser call under any circumstances.

24. **Select-all button wiring: the parent must pass `onToggleAll`.** When a child component (like `PermissionCatalogList`) exposes a select-all callback via `onAllSelectedChange({ allSelected, toggleAll })`, the parent must pass `onToggleAll(perms, checked)` to the child for the toggle to actually do anything. Common bug: the parent renders the select-all button in its own `action` prop but never passes `onToggleAll` to the child — the button renders, the user clicks it, nothing happens. Always check both directions: (a) the child receives `onToggleAll`, and (b) the parent's `toggleAll` callback (from `onAllSelectedChange`) actually calls `onToggleAll` with the right arguments.

25. **Subagent implementation verification.** When delegating implementation to a subagent (orchestrator), the subagent may not commit its changes. After the subagent finishes, you MUST: (a) verify the changes are present on disk by re-reading key files, (b) run lint + build + relevant tests, (c) commit yourself. Do not assume the subagent left the working tree clean or the code in a passing state. Re-read key files to confirm the subagent's changes match the design decisions. This is especially important for multi-file changes where the subagent may have missed a file or left stale imports.

26. **MUI ListItemButton + nested `<a>` elements.** See `references/mui-listitembutton-nested-link.md` for the full pattern and fix.

27. **Spanish/English permission key mismatch (`view` vs `ver`).** See `references/spanish-english-permission-names.md` for the full list of affected files and the fix.
