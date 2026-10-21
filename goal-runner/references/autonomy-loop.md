# Running the Autonomy Loop

The loop is small. Its discipline is in what gets written down after each lap, because that is what survives a cut turn.

## The Lap

```
plan → act → verify → record → plan …
```

1. **Plan.** Read `STATE.md`. Take its single next action. If the action no longer matches reality, update it first — do not act on a stale plan.
2. **Act.** Do the whole action. A half-applied edit, a placeholder, or a skipped edge case is not a lap; it is a future failure with extra steps.
3. **Verify.** Run every gate the action could have changed, fresh, from its declared cwd. A change to shared code can touch gates other than the one being targeted.
4. **Record.** Append results to `EVIDENCE.md`. Rewrite `STATE.md` with the new gate status, iteration count, strategy, blockers, backlog, and the next action.
5. **Continue.** Start the next lap. No check-in between laps.

A lap that ends with no gate result and no new information is a wasted lap. Count it anyway, and let the no-progress guard catch the pattern.

## The Next Action

`STATE.md` is only as good as its next action. A cold start must be able to execute it without the chat history.

Format:

```
<verb> <object> in <path> — <command or exact edit>; done when <observable>
```

Good:

- `Edit src/export.py to quote fields containing comma, quote, or newline — run python3 -m pytest tests/test_export.py -q; done when G2 is green.`
- `Run python3 -m tasks export --format csv --filter done=false and capture the first line; done when it equals id,title,status,created_at.`
- `Read src/report.py:40-90 to locate the filter predicate, then change the export query to reuse it; done when G1 prints exactly the 3 fixture rows.`

Bad:

- `Continue with the export.`
- `Fix the failing tests.`
- `Look into the error.`
- `Finish the remaining work.`

The test: could another agent, with only `.goal/`, start the command or edit without asking a question? If not, sharpen it.

## What Goes Where

| Information | File | Mode |
|---|---|---|
| Goal, criteria, gates, no-goals, constraints, assumptions, budget, amendments | `GOAL.md` | Frozen; amendments only |
| Current plan, gate status, iteration, strategy, blocker, backlog, next action | `STATE.md` | Snapshot; rewritten after each lap |
| Command, cwd, exit code, output, timestamp, verdict | `EVIDENCE.md` | Append-only |
| A hard block, options, recommendation, resume steps | `HANDOFF.md` | Written once per block |

`STATE.md` is a snapshot because a cold start needs the current truth, not the history. `EVIDENCE.md` is a log because a verdict is only trustworthy if the run behind it is still visible.

Write both after every lap. A run that updates state "at the end" loses everything when the end never arrives.

## Evidence Discipline

One entry per gate run:

```markdown
## 2026-10-21T14:03:11Z — G2 — pass

- Cwd: `/repo`
- Command: `python3 -m pytest tests/test_export.py -q`
- Exit: 0
- Output:
  ```
  1 passed in 0.42s
  ```
```

Rules:

- Record failures too. A red entry with the error is what makes the next strategy possible; a log of only passes hides the run.
- The command is copied exactly as run, including flags and environment prefixes.
- Output is the decisive excerpt, not a truncated guess. Long logs go to a file; the entry names the file and quotes the line that decided the verdict.
- Redact secrets as `<redacted>` and name the variable, never the value.
- Never edit or delete an entry. A wrong entry is corrected by a new one that says what it supersedes.
- The final pass gets its own entries. Evidence from lap 3 does not prove the artifact at lap 9.

An entry without exit code or command is a note, not evidence.

## No-Progress Guard

Track in `STATE.md`:

```
- Strategy: A — serialize rows with the stdlib csv module
- Same-failure count: 2
- Failure signature: G2 — ModuleNotFoundError: No module named 'pandas'
```

The failure signature is the gate plus the error class, not the full traceback.

- **Three consecutive laps with the same signature and no gate flipping green** → change strategy. Reset the count when the strategy changes.
- A strategy change alters the mechanism: a different library, a different design, a different decomposition, a different diagnostic path. Re-running the same command with a cosmetic tweak is not a strategy.
- Name strategy A when the first approach starts, and strategy B when A fails. Record what each tried and why it failed.
- **Two exhausted strategies, or six laps on one failure without a green flip** → handoff. The goal may still be achievable; the run has proven it cannot find the way from here.
- A flaky gate gets one re-run. Two identical failures are red, not flaky.
- A gate flipping green resets the no-progress counters and updates the plan.

The guards exist so the run ends honestly instead of spinning. A handoff after six focused laps is a result; a fortieth retry is not.

## Scope Guard

Every discovery lands in exactly one bucket:

1. **Required by a done criterion** → add it to the plan and continue.
2. **Blocks a green gate** (a broken fixture, a missing test dependency, a wrong path) → fix it, and record why in `STATE.md`.
3. **Neither** → append to `Backlog` with enough context to act later: file, symptom, and why it is out of scope now.

The backlog is not a suggestion list for this run. It is the place where good ideas wait so the goal can finish. Implementing a backlog item silently spends the budget on work nobody asked for; deleting it loses information the user may want.

Before claiming done, compare the actual diff against `GOAL.md`. Changes that no criterion requires and no gate needs are scope drift, even when they are improvements.

## Turn and Session Boundaries

The skill does not create turns. The harness decides when a turn ends, and a model cannot run in the background. What the skill controls is what is left behind.

- **Within a turn** — work until all gates are green or a hard block appears.
- **Across turns** — `STATE.md` holds the next action and last verified state. A later turn continues from it.
- **Across sessions** — a cold start reads `.goal/<slug>/`, re-verifies the last gate, and continues. No chat history is required.

If the harness cuts the turn mid-lap, the last recorded state wins. Re-run the gate that was in progress; do not assume the action completed.

If a context compaction occurs, re-read `STATE.md` and the tail of `EVIDENCE.md` before acting. Memory of gate status is not a source of truth.

If the user sends a message mid-goal:

- A question or comment that does not change the goal: answer it, then continue. A check-in is not a stop order.
- A change to scope or acceptance: record it as a user amendment in `GOAL.md`, update the plan, and continue.
- A request to stop: stop. Record the status and leave the state resumable.

Never end a turn with "shall I continue?", "should I proceed?", "let me know if you want me to keep going", or a progress summary that reads like a final report. End with a green verification, a handoff, or a state written for the next turn.

## Cold Start Procedure

Read in this order:

1. `HANDOFF.md` — if present, the run is blocked; check whether the block has been cleared.
2. `GOAL.md` — the frozen acceptance.
3. `STATE.md` — the plan, status, and next action.
4. The tail of `EVIDENCE.md` — what the last runs actually showed.

Then:

1. Re-run the last gate named in `STATE.md`, fresh.
2. If it differs from the recorded status, the disk is right. Update `STATE.md` and act on the fresh result.
3. If `EVIDENCE.md` is missing or was truncated, every gate is unproven: re-run them before any done claim.
4. If `GOAL.md` says `done`, run every gate fresh. All green → confirm done with new evidence. Any red → reopen the goal, record the failure, and repair. A done claim is only as good as its last verification.
5. If `GOAL.md` is missing, do not invent a contract. Report the corruption and stop. Reconstructing acceptance from memory is how a goal quietly changes shape.
6. Continue at the next action. Do not restate the plan to the user, re-ask a settled decision, or start from a blank slate.

A resume is successful when the first tool call after reading is the recorded next action or the re-verification of the last gate — not a question.

## Anti-Patterns

| Symptom | What it means | Fix |
|---|---|---|
| `STATE.md` updated only at the end | Nothing survives a cut | Write after every lap |
| Gate marked green with no fresh evidence line | Memory is doing the verification | Re-run and append |
| Next action names an intention, not a step | Cold start will stall | Name the file, command, and observable |
| Same error on the fourth attempt | The guard was not counted | Switch strategy or hand off |
| Backlog empty after a long run | Discoveries were implemented or forgotten | Re-read the diff and the notes |
| Handoff lists one option | The human is asked to rubber-stamp | Give real alternatives and a recommendation |
| The report says "all tests pass" with no command | The claim is unverifiable | Quote the command and output |
| A run "waits" for the user between laps | The loop stopped without a block | Continue or hand off |
