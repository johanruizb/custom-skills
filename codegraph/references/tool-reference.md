# CodeGraph tool reference

Lookup material for `codegraph/SKILL.md`. The skill body owns the routing; this file owns exact flags, status fields, failure messages, and freshness banners.

## CLI commands

Run `codegraph <command> --help` for the full flag list. The ones that matter here:

| Command | Use | Key flags |
|---|---|---|
| `codegraph explore "<query>"` | Same output as `codegraph_explore`: source, call paths, blast radius. | `-p/--path`, `--max-files` |
| `codegraph query <term>` | Symbol search. | `-p/--path`, `-l/--limit`, `-k/--kind`, `-j/--json` |
| `codegraph node <symbol>` | One symbol's source plus caller/callee trail. | `-p/--path`, `-f/--file` |
| `codegraph node --file <path>` | File with line numbers and dependents. | `--offset`, `--limit`, `--symbols-only` |
| `codegraph callers <symbol>` | Functions/methods that call it. | `-f/--file`, `-l/--limit`, `-j` |
| `codegraph callees <symbol>` | Functions/methods it calls. | `-f/--file`, `-l/--limit`, `-j` |
| `codegraph impact <symbol>` | Affected symbols before a change. | `-f/--file`, `-d/--depth`, `-j` |
| `codegraph affected [files...]` | Test files affected by changed source. | `--stdin`, `-d/--depth`, `-f/--filter`, `-q/--quiet`, `-j` |
| `codegraph files` | Indexed file tree. | `-p`, `--filter`, `--pattern`, `--format`, `--max-depth`, `-j` |
| `codegraph status [path]` | Index health. | `-j/--json` |
| `codegraph context <task>` | Broader task bundle; use sparingly. | `-f/--format`, `-n/--max-nodes`, `--no-code` |
| `codegraph sync [path]` | Incremental update. | `-q/--quiet` |

Index lifecycle commands (`init`, `index`, `uninit`, `unlock`, `upgrade`, `install`, `uninstall`) are outside this skill. Use them only on an explicit request.

## MCP surface

Default tool: `codegraph_explore`.

Input schema:

- `query` (string, required): symbol names, file names, short code terms, or a natural-language question.
- `maxFiles` (number, default 12): cap on files with source.
- `projectPath` (string): target a project with a `.codegraph/` index when the server has no default project or you are querying a second project.

Other tools (`codegraph_search`, `codegraph_node`, `codegraph_callers`, `codegraph_callees`, `codegraph_impact`, `codegraph_files`, `codegraph_status`) are defined but unlisted by default. Enable them with `CODEGRAPH_MCP_TOOLS=explore,node,search,...` if the host supports it; otherwise use the CLI.

If the tool is listed but deferred, load it by name through the host's tool search. If it still is not available, use the CLI.

## Status fields (`codegraph status -j`)

| Field | Meaning |
|---|---|
| `initialized` | An index exists. |
| `projectPath`, `indexPath` | Resolved project and `.codegraph/` path. |
| `lastIndexed` | ISO timestamp of the last completed index. |
| `fileCount`, `nodeCount`, `edgeCount` | Index size. |
| `pendingChanges` | `{added, modified, removed}` since the last sync. Non-zero means the structure is stale. |
| `worktreeMismatch` | Non-null when the index belongs to another worktree. Query the right path or re-index with consent. |
| `index.state` | `complete` or a catch-up state. |
| `index.reindexRecommended` | Version or extraction mismatch; a full re-index is a user decision. |
| `languages`, `nodesByKind` | Coverage. |

The human `codegraph status` prints `Index is up to date` when `pendingChanges` is zero.

## Failure modes

**No index.** `codegraph explore` prints `CodeGraph isn't available here...` and exits **1**. Read the message rather than retrying or treating it as a graph answer. Stop calling CodeGraph for that project and use built-in tools. The project owner can run `codegraph init`; do not run it yourself.

**Empty result.** `No relevant code found`. The match is lexical; retry with literal names or the suggested candidates.

**Missing symbol in a flow.** The graph reports a missing symbol with did-you-mean suggestions. Query the suggested name explicitly; partial or mistyped names are not silently substituted as flow endpoints.

**Ambiguous symbol.** `callers`, `callees`, and `impact` accept `-f/--file` to narrow definitions. `node` accepts `-f` too.

**Stale index.** `pendingChanges` is non-zero, or a banner appears. The source may be current; the structure is not. CLI: `codegraph sync <project>`. MCP: wait for auto-sync; if the banner says disabled or recovering, sync or read files.

**Locked index.** Indexing reports a lock. `codegraph unlock <path>` removes a stale lock. Use it only after a failed index or sync; do not delete `.codegraph/` by hand.

**Daemon.** `codegraph daemon` is interactive (pick one and press enter). Do not run it in a non-interactive shell. Inspect with `pgrep -af codegraph` or use `status`.

**Worktree mismatch.** `worktreeMismatch` is non-null; the index belongs to another worktree. Query the right path or re-index with consent.

## Freshness banners

- `Some files referenced below were edited since the last index sync` — the listed files are pending. Read those specific files; unflagged files are trustworthy.
- `CodeGraph auto-sync is DISABLED` or `RECOVERING` — the whole index may be stale. Read directly until catch-up finishes.
- `changed on disk after the last index sync` — the file drifted. The response shows its full current source (trust it as a Read) or omits it (Read that file); line numbers elsewhere may shift.
- `Already sent earlier in this conversation` — only with `CODEGRAPH_EXPLORE_DEDUP=1`. It points to exact, unchanged source from an earlier call; use that copy and do not re-fetch or Read.
- A response that refuses to answer from changed files because freshness could not be verified is not an error. Retry after sync or narrow the query.

## Cost

CodeGraph reduces discovery calls but returns dense payloads that stay in the context window. Prefer the narrowest query: `node`, `query`, `callers`, `callees`, or `impact` for one symbol instead of exploring a subsystem. In a long session with a small window, budget for the residual context.
