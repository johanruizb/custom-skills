# The Goal Contract

The contract is the part of the run that cannot move while the work is inconvenient. It answers one question before any code changes: **what would make this goal finished, and how would we know?**

A contract that is vague, unverifiable, or quietly editable turns the loop into a confident guess. Spend the time here.

## Anatomy

`GOAL.md` holds, in order:

1. Goal sentence.
2. Done criteria, `D1…Dn`.
3. Gates, `G1…Gn`, each mapped to the criteria it proves.
4. No-goals.
5. Constraints.
6. Assumptions.
7. Budget and stop conditions.
8. Optional subgoals.
9. Amendments.

The file is frozen before work starts (end of Phase 2). From then on, changes go through the Amendments table with a date and a reason.

## Goal Sentence

One sentence, one outcome, observable from outside the implementation.

| Weak | Strong |
|---|---|
| Improve the exporter | `tasks export --format csv` prints RFC 4180 CSV for the filtered table |
| Work on onboarding | A new user completes signup and lands on the dashboard with a session cookie |
| Fix performance | The dashboard's p95 load time on the fixture dataset is under 800 ms |

The strong version names the artifact, the behavior, and the condition. It also implies the gate. If you cannot write the gate, the sentence is still too vague.

Do not put a method in the goal sentence unless the method is the requirement. "Use Redis for caching" is a constraint; "the endpoint returns cached results in under 50 ms on the second call" is the outcome.

## Done Criteria

Each criterion is an end state, not a task. Tasks belong in `STATE.md`; criteria belong in `GOAL.md`.

A criterion is well formed when:

- **Observable** — someone who was not in the session can check it from the artifact.
- **Outcome-shaped** — it describes the result, not the effort. "Parser handles quoted newlines" beats "implement quoting".
- **Independent of implementation** — it survives a rewrite. Test behavior, not a function name.
- **Covered** — together the criteria cover the whole request, including its stated constraints.
- **Necessary** — each one is required by the request or by a correctness constraint. A criterion invented to make the report look fuller is scope drift.

Coverage beats count. One criterion with three gates is better than three criteria that restate the same behavior.

Where a requirement is qualitative (wording, visual hierarchy, API ergonomics), make it as observable as possible: name the states, the audience, the checklist, or the reference. If judgment is irreducible, say so and use a manual gate.

## Gates

A gate turns a criterion into a decision. The default is runnable:

```
### G2 — covers D2

- Check: `python3 -m pytest tests/test_export.py -q`
- Cwd: `/repo`
- Expect: exit 0; output ends with `1 passed`
- Timeout: 120s
- Manual: no
```

Both halves matter. Exit code alone misses a command that succeeds while printing the wrong thing; output alone misses a crash that printed the expected token earlier. Require the expected exit code **and** a decisive output token.

### Command hygiene

- **Declare the cwd.** Relative paths resolve from it, and a gate run from the wrong directory is a different test.
- **Make the status real.** In a pipeline, `cmd | tail` returns `tail`'s status. Use `set -o pipefail` (bash), capture output to a file and check `$?`, or run the command without a pipe. Never append `|| true`.
- **Be deterministic.** Pin the seed, freeze time, clear the cache when the criterion depends on a cold path, and avoid the network unless the network is the subject.
- **Isolate ambient state.** Pass required env vars explicitly; do not depend on a shell profile, a global install, or a service that happens to be running.
- **Be idempotent.** Running the gate twice must produce the same verdict. If the gate mutates state (a build, a migration), say what it changes and how to reset.
- **Bound it.** Set a timeout. A hanging gate is red, not pending.
- **Keep the output inspectable.** Capture long output to a file; print the decisive excerpt. The evidence entry needs enough to reproduce the verdict, not a megabyte of logs.
- **Prefer the project's own entry points.** `npm test`, `make check`, `./scripts/verify.sh` survive refactors better than a hand-built pipeline.

### Failure modes to reject at authoring time

| Gate | Why it cannot prove anything |
|---|---|
| `echo done` / `true` | No observation. |
| `test -f out.csv` | Proves a file exists, not that it has the right rows. |
| `grep -q header out.csv` where the command created `out.csv` | The command under test can write anything. |
| `cmd \| tail -1` | Returns `tail`'s exit status; failures disappear. |
| `cmd \| grep expected` | `grep` succeeds on a matching warning from a failed run. |
| `cmd \|\| true` | Erases the failure. |
| A check on a proxy (line count, file size) | Measures a side effect, not the criterion. |
| A check that passes before the work | Either the criterion is already met or the gate is measuring something else. |

### Negative controls

For a gate that proves **absence** (no secrets, no broken links, no forbidden imports), run it once against a known violation. If it stays green on the positive control, it cannot fail. Record the control in the evidence entry.

For a gate that proves **presence**, the empty or placeholder implementation is the negative control: it must be red. Run it before the work.

### Manual gates

Use one only when no command can decide the outcome. Then make the judgment as narrow as possible:

```
### G4 — covers D3

- Check: none.
- Manual: yes — visual hierarchy at 1440×900 cannot be decided by a command.
- Evidence: screenshot of `/dashboard` at 1440×900, default and empty states, attached path.
- Judge: the user.
```

Evidence should scale with risk. A low-risk wording check needs one artifact and one sentence of judgment. A security, data-loss, or public-API decision needs an independent reviewer, multiple states, and an explicit checklist.

A failing runnable gate never becomes manual. That conversion is a weaker acceptance dressed as a format change.

### The gate review

Before freezing, ask of every gate:

1. Would this be red if the feature were absent or broken? If not, it is not a gate.
2. Does it measure the criterion or a convenient neighbor?
3. Could it pass for the wrong reason (stale artifact, cached build, warning text, exit code of another process)?
4. Can a cold start run it from the written instructions alone?

Fix the gate or the criterion — in that order.

## No-Goals

No-goals protect the run from its own momentum. Write what is explicitly out of scope, especially the adjacent things a competent agent would otherwise improve:

- No schema changes.
- No new runtime dependency.
- No UI changes outside the export button.
- No refactor of the reporting module.

When a discovery falls under a no-goal, it goes to `Backlog` in `STATE.md`, not into the change.

## Constraints

The conditions the solution must respect: language and runtime versions, compatibility, performance envelope, files that must not change, deadlines, deployment target, licensing. Constraints are part of acceptance; a result that violates one is not done even if every functional gate is green.

Where a constraint is checkable, give it a gate too (for example, "no new dependency" checked against the lockfile diff).

## Assumptions

Underspecified requests need decisions. Record them instead of asking:

```
- A1 — The export reuses the existing `--filter` syntax; no new filter parser.
  If wrong: the command accepts only the documented flags and needs a follow-up.
```

Record only assumptions that are reversible at the cost of rework, not data loss or an incompatible public interface. An assumption that could invalidate the deliverable is a handoff condition, not a silent choice.

## Budget and Stop Conditions

The budget is what turns "keep going" into a bounded run:

```
- Max iterations: 12 laps
- Max wall-clock: 90 minutes
- Stop conditions: all gates green; a hard block (see references/handoff.md); budget spent.
```

Count a lap every time the loop plans, acts, verifies, and records — not every tool call. When the budget is spent with red gates, write the handoff. Never present a partial result as done because the clock ran out.

Set the numbers from the size of the goal, not optimism. A one-file fix with three gates does not need fifty laps; a migration with subgoals may need more than twelve.

## Amendments

The contract is frozen, not petrified. Change it only through the table:

| Date | Change | Reason |
|---|---|---|
| 2026-10-21 | G2 uses `pytest -q tests/test_export.py` after the suite split | The original path no longer exists; the criterion is unchanged |

Allowed without asking:

- The world changed: a path moved, a dependency was renamed, an API version shifted. Update the command so it still measures the same criterion.
- The original gate measured a proxy. Replace it with a check that is at least as strict and record why.
- The user explicitly changed the scope. Record their change verbatim.

Forbidden:

- Dropping a done criterion because it is hard.
- Lowering a threshold or relaxing an expected result.
- Converting a runnable gate to manual after it failed.
- Deleting a failed gate or editing `EVIDENCE.md`.

The last four weaken acceptance. An agent-initiated weakening is a goal change and goes to handoff. A user-initiated change is recorded as an amendment and the run continues.

After an amendment, update the freeze date and re-run any gate whose command changed.

## Subgoals (Optional)

Decompose only when the goal has several independently deliverable outcomes, or when dependencies make integration a real risk. A single-deliverable goal stays a single contract.

Keep the subgoals in the same `GOAL.md`, not in nested `.goal/` folders:

| ID | Deliverable | Depends on | Gates | State |
|---|---|---|---|---|
| S1 | CSV serializer | — | G1, G2 | pending |
| S2 | CLI flag and wiring | S1 | G3, G4 | pending |
| S3 | Docs and end-to-end | S1, S2 | G5 | pending |

Rules:

- Each subgoal has its own done criteria and gates. A leaf is integrated only after its gates are green fresh.
- A dependency is satisfied by evidence, not by a subagent's report.
- The integration gate re-runs the leaf gates and exercises the end-to-end path. The goal is done only when the integration gate is green.
- Keep one `STATE.md`. Its plan orders the leaves; it does not duplicate every leaf's internals.

Depth that buys nothing is a second plan to maintain.

## Worked Example

A small but complete contract for a CLI feature:

```markdown
# Goal: Add `tasks export --format csv`, which writes the filtered task table to stdout as RFC 4180 CSV.

## Done criteria
- D1 — The command prints a header row and one row per filtered task.
- D2 — Commas, quotes, and newlines in fields are quoted and round-trip through a CSV reader.
- D3 — `tasks list` and the existing test suite behave exactly as before.

## Gates
### G1 — covers D1
- Check: `python3 -m tasks export --format csv --filter done=false`
- Cwd: `/repo`
- Expect: exit 0; first line `id,title,status,created_at`; 3 data rows for the fixture.
- Manual: no

### G2 — covers D2
- Check: `python3 -m pytest tests/test_export.py -q`
- Cwd: `/repo`
- Expect: exit 0; output ends with `1 passed`
- Manual: no

### G3 — covers D3
- Check: `python3 -m pytest -q`
- Cwd: `/repo`
- Expect: exit 0; no `failed`
- Manual: no

## No-goals
- No storage schema change.
- No new runtime dependency.
- No change to the web UI.

## Constraints
- Python 3.11; standard library `csv` module.
- Exit code 2 for an unknown format.

## Assumptions
- A1 — `--filter` keeps its existing syntax.

## Budget
- Max iterations: 10
- Max wall-clock: 60 minutes
- Stop conditions: all gates green; hard block; budget spent.
```

The example is small on purpose. Most goals need three to six criteria; more usually means the goal should be split.
