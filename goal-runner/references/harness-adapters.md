# Harness Adapters

The core of goal-runner names capabilities, not tools. This file maps those capabilities to concrete harnesses. Load the section that matches the environment; skip the rest.

## Capability Map

| Capability | Used for | Required |
|---|---|---|
| `file_read` | Reading `GOAL.md`, `STATE.md`, `EVIDENCE.md`, and the code under change | Yes |
| `file_write` | Creating and updating the four state files | Yes |
| `file_search` | Locating code, tests, and prior evidence | Yes |
| `cmd_exec` | Running gates, inspecting results, building the artifact | For runnable gates |
| `dir_list` | Surveying the repo and `.goal/` | Yes |
| `subagent` | Optional decomposition into independent leaves | No |
| `user_channel` | Delivering the handoff or the final report | Yes |

If `file_write` is missing, do not start: the run cannot persist, so the resume promise is false. If `cmd_exec` is missing, the run can only use manual gates; say so before freezing the contract, because the verification is weaker than the skill's default.

## OpenCode

Tools: `read`, `write`, `edit`, `bash`, `glob`, `grep`; optional `todowrite` and `task`.

- **State location.** Use `.goal/<slug>/` at the repository root. If the session's working directory is a subdirectory, resolve the root first (`git rev-parse --show-toplevel` or the workspace root). Do not scatter state across subprojects.
- **Persistence.** Write each file with `write` or `edit`; there is no hidden memory to rely on. The session may be compacted at any point, and after compaction only the files remain.
- **Turn boundary.** A turn ends when the assistant returns a response. OpenCode does not keep the agent running in the background. Write `STATE.md` after every lap so the next turn — same session or new — starts from disk.
- **Compaction.** When the context is compacted, re-read `STATE.md` and the tail of `EVIDENCE.md` before the next action. Do not reconstruct gate status from memory.
- **Permissions.** OpenCode may ask the human to approve shell commands or file writes. That is the harness's permission layer, not the skill asking for approval. The run cannot bypass it: if every command prompts, the human must pre-approve the workspace or the run will stall. Never use bypass flags or disable permissions to keep going.
- **Subagents.** `task` starts a fresh context. Give a subagent the absolute `.goal/<slug>/` path and a single independent leaf; it writes evidence, the parent re-runs the leaf gates. Two agents must not write the same `STATE.md` concurrently. A subagent's done claim is not evidence.
- **Todo list.** `todowrite` is a live convenience, not state. The plan of record is `STATE.md`.
- **Commits.** Follow the repository's own policy. If it requires a commit at the end of a turn, commit the work; include `.goal/` only when it is tracked by that repository's convention.

## Claude Code

Tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, optional `Task` and `TodoWrite`.

- Same state layout and turn rules. A subagent's result returns to the parent, which re-runs the gates.
- Stop hooks, if installed by other skills, are a backstop, not part of this skill. Do not install one to make goal-runner work.
- Auto-compaction keeps the files and drops the conversation; re-read state afterwards.

## Codex and Other CLI Agents

- Use the shell for reading, writing, and running gates; use the patch mechanism for edits when available.
- These harnesses often have no skill router. Point the agent at this `SKILL.md` explicitly, or reference it from `AGENTS.md`.
- Turn boundaries are usually one response. The state files carry everything.
- If the environment is sandboxed without network, gates that need network are red by definition; that is a missing-access handoff if the criterion requires them.

## Editor-Integrated Agents

Cursor, Windsurf, Copilot, and similar agents have file and terminal tools under different names. Map the capabilities, keep the same `.goal/` layout, and confirm the agent can write files and run the gate commands before freezing the contract.

## Portability

- **Shell.** `set -o pipefail` is bash. POSIX `sh`, `cmd.exe`, and PowerShell behave differently. Prefer the project's own check script (`make check`, `npm test`, `./scripts/verify.sh`), which encodes the shell for you.
- **Paths.** Gates declare an absolute cwd or a repo-relative one with the root stated. Windows paths need quoting that POSIX does not.
- **Timeouts.** Every harness has a different default. Put the timeout in the gate and pass it to the command when the harness supports it.
- **Output.** Capture long output to a file; quote the decisive line in `EVIDENCE.md`. Do not paste secrets.
- **Processes.** Stop dev servers, watchers, and background jobs when the lap no longer needs them. A gate that leaves a server running makes the next run depend on ambient state.

## When the Harness Cannot Do It

State the limitation before starting, not after failing:

- No `file_write` → the goal cannot persist or resume. Run it as a one-turn task or decline.
- No `cmd_exec` → only manual gates. Record that verification rests on artifacts and judgment.
- No network → live integration gates cannot run. A missing credential or network path is a handoff if the criterion requires it.
- Read-only filesystem → no contract, no evidence. Stop and say why.

No helper script is required by this skill. The gates are the project's own commands, and a wrapper would add a layer between the evidence and the thing it measures. Add one only if a real gate proves too ambiguous to express as a command; the justification belongs in that goal's `GOAL.md`.
