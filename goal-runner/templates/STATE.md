# State Template

Copy to `.goal/<slug>/STATE.md`. Rewrite it after every lap and before any yield. It is a snapshot of the present, not a log: history belongs in `EVIDENCE.md`.

---

# State: <slug>

- Updated: `<ISO 8601 timestamp>`
- Status: `active | done | blocked`
- Iteration: `<n>` / `<max laps>`
- Budget used: `<minutes elapsed, or time remaining>`
- Strategy: `<A — name of current approach | B — name>`
- Same-failure count: `<n>`
- Failure signature: `<gate + error class, or none>`

## Plan

- [x] **P0** — <completed step> (closed G1)
- [ ] **P1** — <next step> (closes G2)
- [ ] **P2** — <later step> (closes G3)
- [ ] **P3** — final pass: re-run every gate fresh (closes all)

## Current

- In progress: <what is half-done, or none>
- Last fresh gate: `<G#>` — `green | red` — <timestamp>
- Next action: `<verb> <object> in <path> — <command or exact edit>; done when <observable>`

## Gate status

| Gate | Covers | Status | Last fresh run | Evidence |
|---|---|---|---|---|
| G1 | D1 | `green` | <timestamp> | `EVIDENCE.md` <timestamp> |
| G2 | D2 | `red` | <timestamp> | `EVIDENCE.md` <timestamp> |

## Blockers

- `none`

<!-- If blocked, name the exact command and error. Write HANDOFF.md, then set Status: blocked. -->

## Backlog

<!-- Discovered, not required by any done criterion, not blocking a gate. Not implemented in this run. -->

- <file/symptom and why it is out of scope now>
