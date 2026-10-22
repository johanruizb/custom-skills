---
name: codegraph
description: "Use CodeGraph correctly in a project that has a `.codegraph/` index, or when the user mentions CodeGraph / code graph / grafo de código. Routes structural questions (understand, locate, trace, survey, pre-edit impact) to `codegraph_explore` over MCP when available, or `codegraph explore` on the CLI, before grep/glob/read; treats the returned source as already read; enforces freshness, per-project indexes, and the rule that indexing is the user's decision. Triggers: 'usa codegraph', 'consulta el grafo', 'cómo funciona codegraph', 'code graph', 'why didn't you use codegraph'."
license: MIT
metadata:
  author: johanruizb, Hermes Agent
  version: "1.0.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [codegraph, code-intelligence, knowledge-graph, code-navigation, context-efficiency, mcp, cli]
    related_skills: [code-health]
---

# codegraph

## Overview

CodeGraph is a local SQLite knowledge graph of a project's symbols, call edges, imports, and files. It is built per project into `.codegraph/` and answers structural questions from that index. `codegraph_explore` returns the relevant symbols' verbatim, line-numbered source grouped by file, the call paths between them (including dynamic-dispatch hops), and a blast-radius summary.

Treat the returned source as already read. It is re-read from disk and is current; the structure around it comes from the index and can lag writes.

CodeGraph is not a compiler, test runner, linter, or full-text search engine. It supplements those tools; it does not replace them.

## When to Use

- A project has a `.codegraph/` index and the task requires understanding, locating, tracing, surveying, or changing its code.
- The user mentions CodeGraph, "code graph", "grafo de código", "consulta el grafo", "usa codegraph", or asks why you did not use it.
- You are about to explore an indexed codebase with grep/glob/read and one graph query can answer the question.
- A monorepo has an index in a subproject and the task targets that subproject.

Don't use for:

- A project with no `.codegraph/` index and no request to explain CodeGraph. Use built-in tools; indexing is the user's decision.
- Configs, docs, generated files, lockfiles, or literal strings the graph does not index. Use grep/read.
- A single known file or line where a direct Read is cheaper than a dense graph payload.
- Correctness validation. The compiler, tests, and linter still own that.
- Installing, wiring, or indexing CodeGraph. That is outside this skill.

## Phase 1: Preflight

1. Resolve the project root for the task: the nearest ancestor of the target path that contains `.codegraph/codegraph.db`. Do not assume the current directory.
2. If no index exists, stop calling CodeGraph for that project in this session and use built-in tools. If it is relevant, mention once that the project owner can run `codegraph init`; never run it yourself.
3. If the index exists, choose the transport:
   - MCP `codegraph_explore` when the host exposes it. Load it by name if it is deferred. Pass `projectPath` to the indexed project; the MCP server may have no default project.
   - CLI `codegraph` when MCP is unavailable, or for the narrow commands the MCP server does not list.
4. Run `codegraph status -j <project>` when the response banner does not settle freshness and the answer depends on structure: first query of a task, after a branch switch, a large edit, or before a risky change. Read `pendingChanges`, `index.state`, `reindexRecommended`, and `worktreeMismatch`. Do not run it before every query.

**Completion criterion:** you know the indexed project path, whether the index exists, which transport you will use, and whether the graph is fresh enough for the task.

## Phase 2: Graph first

Before the first grep/glob/read of indexed code, call `codegraph_explore` (MCP) or `codegraph explore` (CLI). One call usually answers the whole question.

| Need | MCP (default surface) | CLI |
|---|---|---|
| Understand, locate, survey, or trace a flow | `codegraph_explore` | `codegraph explore "..."` |
| Exact symbol search or name filter | explore with the names | `codegraph query <term> --kind function --limit 10` |
| One symbol or file, with dependents | explore naming it | `codegraph node <symbol>` or `codegraph node --file <path>` |
| Direct callers or callees | explore's blast radius | `codegraph callers <symbol>` / `callees <symbol>` |
| Impact radius before a change | explore's blast radius | `codegraph impact <symbol> --depth 2` |
| Affected tests | not exposed | `codegraph affected <files> --quiet` |
| Indexed project layout | `codegraph_files` if enabled | `codegraph files` |
| Health and freshness | `codegraph_status` if enabled | `codegraph status -j` |

The MCP default surface exposes only `codegraph_explore`; the other tools are defined but unlisted. Use the CLI for those, or enable them with `CODEGRAPH_MCP_TOOLS` when the host supports it.

When delegating exploration to a subagent, put the indexed project path and "use CodeGraph first; treat returned source as read" in the prompt. Subagents see the project instructions file, not the MCP server's initialize guidance.

**Completion criterion:** every structural question in the task has been answered by a CodeGraph call, or by a file the graph flagged as unindexed or omitted; no indexed code was grepped or read before the first graph call.

## Phase 3: Query craft

- Prefer symbol, file, and subsystem names over vague prose. Natural-language questions work, but names retrieve better.
- For a flow, name the symbols that span it (`mutateElement renderScene`), not just "how does this work". Flow endpoints require exact names.
- The match is lexical, not semantic. If a query returns nothing, retry with literal names from the repository or the did-you-mean candidates; do not paraphrase endlessly.
- Qualified names accept `.`, `::`, and `/`.
- Keep the payload narrow: `maxFiles` (MCP, default 12) or `--max-files` (CLI). Query the symbol you need, not the whole subsystem.
- In a monorepo or a second repository, pass `projectPath` (MCP) or `--path` (CLI).
- One targeted call beats a chain of broad calls. If the first call is close, refine the names rather than switching to grep.

**Completion criterion:** the query names the relevant symbols, files, or flow endpoints; the result fits the output cap; and an empty result has been retried with a suggested or literal name.

## Phase 4: Trust and freshness

- Treat every source block returned by `codegraph_explore` or `explore` as already read. Do not re-open or grep those files to verify the graph.
- The source block is re-read from disk and is current. The structure (flow, blast radius, symbol list) comes from the index and can lag writes.
- Read the response banner. A file flagged as edited since the last sync is pending: Read that specific file. A banner saying auto-sync is disabled or recovering means the whole index may be stale: Read directly until catch-up completes. A file flagged as changed on disk either shows its full current source (trust it as a Read) or omits it (Read that file); line numbers referencing it elsewhere may shift until the next sync. Exact text and status fields: `references/tool-reference.md`.
- MCP mode: the server watches and auto-syncs (about one second). After an edit, wait for the sync or follow the banner; do not run `sync` just because you edited.
- CLI-only mode has no watcher unless a CodeGraph daemon or MCP server is running for that project. After editing, run `codegraph sync <project>` before relying on structure. The source block may already be current; the structure is not.
- New, renamed, and deleted files are invisible to the graph until sync. Sync before querying them, or read them directly.
- Use grep/read only for what the graph does not cover: literal strings, configs, docs, generated files, and files the response flagged or omitted.

**Completion criterion:** every returned source block is treated as read, every flagged or omitted file has been read, and no grep or read was used to re-verify a returned block.

## Phase 5: Edit loop

1. Before editing, query the symbols you will change and read the blast radius. For a shared utility or public API, use `codegraph impact` to see the full radius.
2. Edit from the returned source, or from a Read when the file was flagged or omitted.
3. After the edit, follow the freshness rules: MCP waits for auto-sync; CLI runs `codegraph sync <project>` before relying on structure.
4. Re-query only when you need structure you did not already have: a new caller, a changed flow, an impact check. Do not re-query to confirm the edit; the compiler and tests do that.
5. For test selection, `codegraph affected <changed files>` traces import dependencies and auto-detects test files. It narrows the test run; it does not replace the full suite when the change is broad.

**Completion criterion:** the edit was made from fresh source, the blast radius was considered, the index was synced or given time to sync, and correctness was checked with the project's compiler, tests, or linter.

## Phase 6: Report

When CodeGraph was used, include one line in the final response:

`CodeGraph: MCP explore("auth login")` or `CodeGraph: CLI explore + sync`.

When an index existed but you did not use CodeGraph, say why in one line:

`CodeGraph: skipped — literal string search (grep)`.

When there is no index, no line is needed unless the user asked about CodeGraph.

**Completion criterion:** the final response names the CodeGraph call or the reason for the fallback, and no unsupported claim is presented as graph-derived.

## Common Pitfalls

- Grepping first in an indexed project.
- Calling explore and then re-reading the same files to be sure.
- Running `codegraph init`, `index`, or `uninit` without the user's decision.
- Assuming the MCP server has a default project when it has no root index; pass `projectPath`.
- Assuming the CLI auto-syncs. It does not unless a watcher is running; check `pendingChanges` and sync after edits.
- Trusting a stale flow or blast radius because the source block looked current.
- Using CodeGraph for configs, docs, literal strings, or generated files.
- Treating CodeGraph output as correctness proof and skipping tests.
- Querying with vague prose, then concluding "CodeGraph does not know this" after one empty result.
- Dumping a whole subsystem when one symbol would answer the question.
- Delegating to a subagent that re-reads what CodeGraph already returned.
- Committing `.codegraph/`; it is local and self-ignored.

## Verification Checklist

- [ ] Index presence checked at the task's project root, not just the current directory.
- [ ] Transport chosen: MCP explore with `projectPath`, or CLI.
- [ ] First structural question answered by CodeGraph before grep/glob/read.
- [ ] Source blocks treated as read; only flagged or omitted files were Read.
- [ ] CLI-only edits followed by `codegraph sync` before structure queries.
- [ ] No index-building command (`init`, `index`, `uninit`) ran without explicit user consent.
- [ ] Compiler, tests, or linter used where correctness matters.
- [ ] Final response includes the CodeGraph receipt or the fallback reason.
