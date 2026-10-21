# Handoff Template

Copy to `.goal/<slug>/HANDOFF.md` only when one of the three hard blocks applies: missing access, invalidating ambiguity, or budget spent. One file per goal; append a dated section for a later block.

---

# Handoff: <slug>

- Date: `<ISO 8601>`
- Status: `blocked`
- Block kind: `missing access | invalidating ambiguity | budget spent`

## Done

- **D1** — <state>; evidence: `EVIDENCE.md` <timestamp> / <gate>
- **D2** — <state>; evidence: `EVIDENCE.md` <timestamp> / <gate>

## Remaining

- **D3** — <what remains>; next action: `<exact command or edit>`
- Final pass — re-run every gate fresh; next action: `<exact command>`

## The block

<What cannot proceed, and why. One paragraph.>

```
<exact command>
<exact error, with secrets redacted>
```

## Options

1. **<option>** — <what it unblocks>. Cost: <time, money, risk>.
2. **<option>** — <what it unblocks>. Cost: <time, money, risk>.
3. **Do nothing** — <consequence>. (Include only when it is a real option.)

## Recommendation

Option `<n>` — <one sentence: why this one over the others>.

## To resume

1. <The exact value, decision, or permission the human must provide.>
2. Invoke goal-runner on `.goal/<slug>/`; it re-verifies `<gate>` and continues at `<next action>`.

## Do not

- <The tempting shortcut that violates the contract, e.g. hardcode a key, disable a gate, or mark a failed check manual.>

<!-- On resolution, append (do not edit the block above):

## Resolution — <YYYY-MM-DD>

- Provided: <what cleared the block>
- Consequence: <amendment or state change>
- Resumed at: <gate and next action>
-->
