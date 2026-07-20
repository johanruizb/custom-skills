# Harness Adapters

This file contains adapters for each supported harness. Each adapter maps the core capabilities to concrete tools. Load the matching adapter at Phase 1.

> **Sibling skill notice:** `test-suite-improver` (same category) has a copy of this file at its own `references/harness-adapters.md`. When you update this file, mirror the changes there too. The two files are intentionally duplicated (skills cannot share files across directories), but must stay in sync to avoid drift.

## Capability Reference

| Capability | Purpose | Required for |
|---|---|---|
| `file_read` | Read file contents | All phases |
| `file_search` | Search file contents (regex/grep) | Audit, global pattern search |
| `file_find` | Find files by name/glob | Project discovery |
| `file_write` | Edit/create files | Fix application, HTML report |
| `dir_list` | List directory contents | Project discovery |
| `cmd_exec` | Execute shell commands | Linters, tests, build, git |
| `git_query` | Query git history/branches | Context, changed-file detection |
| `web_search` | Search the web | Technical research |
| `web_extract` | Extract web page content | Technical research |
| `user_ask` | Structured user questions | Configuration, fix selection |
| `subagent_spawn` | Delegate to subagents | Parallel audit |
| `task_manage` | Manage todo/task list | Progress tracking |
| `state_persist` | Persist state to disk | Resumption |
| `html_open` | Open HTML in browser | HTML report display |

---

## Hermes Adapter

Hermes exposes: browser tools, terminal, web_search, web_extract, read_file, write_file, patch, search_files, skill tools, delegate_task, clarify, todo, cronjob, memory, execute_code, computer_use, vision_analyze, text_to_speech.

### Capability Map

| Capability | Tool | Notes |
|---|---|---|
| `file_read` | `read_file` | Supports offset/limit for large files |
| `file_search` | `search_files` | target='content' for grep, target='files' for glob |
| `file_find` | `search_files` (target='files') | Glob pattern file search |
| `file_write` | `write_file` / `patch` | patch for targeted edits, write_file for full rewrites |
| `dir_list` | `search_files` (target='files', pattern='*') | List files in a directory |
| `cmd_exec` | `terminal` | Shell execution. Use `background=true` for long-running. Use `pty=true` for interactive. |
| `git_query` | `terminal` (e.g., `terminal(command='git log --oneline -20')`) | Git via shell |
| `web_search` | `web_search` | Returns up to 5 results |
| `web_extract` | `web_extract` | Extracts page content as markdown |
| `user_ask` | `clarify` | Multiple choice (up to 4 options) or open-ended |
| `subagent_spawn` | `delegate_task` | Up to 3 concurrent. Pass `tasks` array for batch. Leaf agents can't delegate further. |
| `task_manage` | `todo` | Task list with status tracking |
| `state_persist` | `write_file` to `.audit-state.json` | Write state to a JSON file in the repo root or temp |
| `html_open` | `terminal` (e.g., `terminal(command='xdg-open /tmp/report.html')`) | Open via shell |

### Hermes-Specific Instructions

- Use `clarify` for ALL user interactions (area selection, fix selection, plan confirmation). It supports `choices` array for multiple selection and open-ended mode for free text.
- Use `delegate_task` with `tasks` array for parallel subagents. Pass full context (project map, version risks, checklists) in each subagent's `context` field. Each subagent returns findings as structured JSON in its summary.
- Use `todo` to track module-level progress. One todo item per module or area.
- For `execute_code`: use it to run the HTML report generator script or to batch multiple `search_files`/`read_file` calls with processing logic.
- For large repos: use `delegate_task` to split module batches across subagents, keeping each subagent's context focused on a subset of modules.
- Use `patch` (not `write_file`) for targeted code fixes — it does fuzzy find-and-replace and runs syntax checks.
- `terminal` is foreground by default and returns instantly when done. Use `timeout=300` for long builds/tests.

### Hermes User Interaction Patterns

```
# Area selection
clarify(
  question="Which areas should the audit cover?",
  choices=["All (performance, bugs, security)", "Performance only", "Bugs only", "Security only"]
)

# Fix selection (after report)
clarify(
  question="Which findings should I fix?",
  choices=["All safe fixes (confirmed, low risk)", "All critical + high severity", "Let me pick by ID", "Audit only — no fixes"]
)

# Plan confirmation
clarify(
  question="Review the audit plan. Proceed?",
  choices=["Yes, proceed as planned", "Adjust scope", "Adjust areas"]
)
```

---

## Claude Code Adapter

Claude Code exposes: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, TodoWrite, Agent/Task (subagents), AskUserQuestion (structured questions with selectable options).

### Capability Map

| Capability | Tool | Notes |
|---|---|---|
| `file_read` | `Read` | Supports `offset` and `limit` |
| `file_search` | `Grep` | Regex content search with `output_mode` |
| `file_find` | `Glob` | Glob pattern file search |
| `file_write` | `Write` / `Edit` | Edit for targeted changes, Write for full files |
| `dir_list` | `Glob` (pattern='*') or `Bash` (`ls`) | |
| `cmd_exec` | `Bash` | Shell execution with timeout |
| `git_query` | `Bash` (e.g., `Bash(command='git log --oneline -20')`) | |
| `web_search` | `WebSearch` | |
| `web_extract` | `WebFetch` | Fetches and extracts page content |
| `user_ask` | `AskUserQuestion` | Structured questions with selectable options |
| `subagent_spawn` | `Agent` / `Task` | Spawn subagents for parallel work |
| `task_manage` | `TodoWrite` | Task list with status |
| `state_persist` | `Write` to `.audit-state.json` | |
| `html_open` | `Bash` (e.g., `Bash(command='open report.html')`) | |

### Claude Code-Specific Instructions

- Use `AskUserQuestion` for all structured interactions. It supports multiple-choice with selectable options.
- Use `Agent` (or `Task`) to spawn subagents for parallel module/area analysis. Each subagent gets a focused prompt with project context.
- Use `TodoWrite` to track audit progress — one item per module/area.
- `Grep` supports `output_mode: "content"`, `"files_with_matches"`, `"count"`. Use `files_with_matches` first to find affected files, then `content` to see evidence.
- `Edit` does targeted find-and-replace with unique string matching. `Write` overwrites entirely.
- `Bash` timeout can be set. Use higher timeouts for test suites and builds.
- For the HTML report: use `Bash` to run the Python generator script, then `Bash(command='open ...')` on macOS or `xdg-open` on Linux.

### Claude Code User Interaction Patterns

```
# Area selection via AskUserQuestion
AskUserQuestion(
  question="Which areas should the audit cover?",
  options=[
    {label: "All", description: "Performance, bugs, and security", value: "all"},
    {label: "Performance", description: "Performance only", value: "performance"},
    {label: "Bugs", description: "Bugs only", value: "bugs"},
    {label: "Security", description: "Security only", value: "security"}
  ]
)
```

---

## OpenCode Adapter

OpenCode exposes: file read, file write/edit, bash (shell), grep/search, glob, web search (if configured), subagent/task spawning, and a TUI-based interaction model.

### Capability Map

| Capability | Tool | Notes |
|---|---|---|
| `file_read` | File read tool | Read file contents |
| `file_search` | Grep/search tool | Content search |
| `file_find` | Glob tool | File pattern search |
| `file_write` | File write/edit tool | Edit or create files |
| `dir_list` | Glob or bash `ls` | |
| `cmd_exec` | Bash | Shell execution |
| `git_query` | Bash (`git ...`) | |
| `web_search` | Web search (if configured) | Check availability at runtime |
| `web_extract` | Web fetch (if configured) | Check availability at runtime |
| `user_ask` | Conversation / structured prompt | OpenCode TUI supports interactive prompts |
| `subagent_spawn` | Task/subagent spawning (if available) | Check at runtime |
| `task_manage` | Todo/task tracking (if available) | Check at runtime |
| `state_persist` | File write to `.audit-state.json` | |
| `html_open` | Bash (`xdg-open` / `open`) | |

### OpenCode-Specific Instructions

- OpenCode's TUI is conversational. If no structured question tool exists, ask via normal conversation.
- Check for web search/fetch availability at runtime — some OpenCode configurations don't include them. If unavailable, note the limitation and reduce confidence on version-specific findings.
- Check for subagent support at runtime. If unavailable, process areas/modules sequentially.
- Use file write to persist state to `.audit-state.json` for resumption support.
- For the HTML report: run the generator script via Bash, then open with `xdg-open`.

---

## Generic Adapter (fallback)

When the harness is not recognized, discover tools by testing each capability:

```
For each capability in the capability table:
  1. Check if the harness documentation mentions a matching tool.
  2. If unclear, attempt to use the tool and catch errors.
  3. Record: available (tool name) or missing (impact on audit).
```

### Generic Fallback Behaviors

| Missing Capability | Fallback | Impact |
|---|---|---|
| `file_read` | Cannot audit. Stop and inform user. | Fatal — audit impossible |
| `file_search` | Read files individually and scan manually | Slower, less thorough pattern detection |
| `file_find` | Use `cmd_exec` with `find` or `ls` if available | Slower discovery |
| `file_write` | Cannot fix or generate HTML report | Audit-only mode forced |
| `dir_list` | Use `cmd_exec` with `ls` if available | |
| `cmd_exec` | Cannot run linters, tests, or builds | Validation limited to manual code review |
| `git_query` | Use `file_read` on `.git/` internals if desperate; usually skip | No git history context |
| `web_search` | Rely on built-in knowledge; reduce confidence on version-specific findings | Stale recommendations risk |
| `web_extract` | Same as web_search | |
| `user_ask` | Ask questions in plain conversation | Less structured, but functional |
| `subagent_spawn` | Process areas/modules sequentially in one agent | Slower, higher context usage |
| `task_manage` | Track progress narratively in responses | Less structured progress tracking |
| `state_persist` | Keep state in context; acknowledge resumption is limited | No resumption after interruption |
| `html_open` | Write HTML file, tell user the path to open manually | User must open manually |

### Generic Detection Heuristics

To detect the harness at runtime:

1. Check for Hermes-specific tools: if `delegate_task`, `clarify`, `todo`, `skill_view` exist → Hermes.
2. Check for Claude Code tools: if `AskUserQuestion`, `TodoWrite`, `Agent` exist → Claude Code.
3. Check for OpenCode: if running inside an OpenCode TUI session → OpenCode.
4. Otherwise: use generic adapter with per-capability probing.

The agent should probe by checking available tool names in its tool list, NOT by calling tools and catching errors (calling tools has side effects). If the tool list is not accessible, probe with a harmless call (e.g., read a known file).