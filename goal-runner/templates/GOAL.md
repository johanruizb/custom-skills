# Goal Contract Template

Copy to `.goal/<slug>/GOAL.md` and fill every section. Write the gates before any implementation, baseline them at the end of Phase 2, then set `Status: frozen`. After that, change the contract only through the Amendments table.

---

# Goal: <one sentence, outcome not activity>

- Slug: `<kebab-case, three words or fewer>`
- Created: `<YYYY-MM-DD>`
- Status: `draft | frozen | active | done | blocked`
- Frozen: `<YYYY-MM-DD or ->`
- Repository: `<absolute path to the repository where the work happens>`

## Goal

<The same sentence, expanded only if a constraint is needed to disambiguate it. One short paragraph maximum.>

## Done criteria

- **D1** — <observable end state a stranger could check>
- **D2** — <observable end state>
- **D3** — <observable end state>

## Gates

### G1 — covers D1

- Check: `<exact command, copied as it will run>`
- Cwd: `<absolute path or repo root>`
- Expect: exit `<code>`; <decisive output: exact token, line, count, or pattern>
- Timeout: `<seconds>`
- Manual: `no`

### G2 — covers D2

- Check: `<exact command>`
- Cwd: `<path>`
- Expect: exit `<code>`; <decisive output>
- Timeout: `<seconds>`
- Manual: `no`

<!-- Repeat for G3…Gn. Every done criterion needs at least one gate. -->

<!-- Manual gate shape, only when no command can decide:
### G4 — covers D3
- Check: none
- Manual: yes — <why no command can decide the outcome>
- Evidence: <artifact, state, viewport, reviewer>
- Judge: <who decides>
-->

## No-goals

- <What this goal explicitly will not change or deliver.>
- <Adjacent improvement that must wait.>

## Constraints

- <Language/runtime versions, compatibility, performance envelope, files that must not change, deadline, deployment target.>

## Assumptions

- **A1** — <decision taken instead of asking>; if wrong, <effect on the deliverable>.
- **A2** — <decision>; if wrong, <effect>.

## Budget

- Max iterations: `<number of laps>`
- Max wall-clock: `<minutes, or an absolute date>`
- Stop conditions: all gates green; hard block per `references/handoff.md`; budget spent.

## Subgoals

<!-- Optional. Remove for a single-deliverable goal. Keep one GOAL.md, no nested .goal/ folders. -->

| ID | Deliverable | Depends on | Gates | State |
|---|---|---|---|---|
| S1 | <deliverable> | — | G1, G2 | `pending` |
| S2 | <deliverable> | S1 | G3 | `pending` |

## Amendments

<!-- Append only. Date, exact change, reason. Never weaken acceptance without the user's explicit decision. -->

| Date | Change | Reason |
|---|---|---|
| — | — | — |
