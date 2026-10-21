# Handoff

A handoff is the one moment the run asks for help. It is a file, not a conversation, and it is written only when the work cannot honestly continue.

The point is not to report difficulty. The point is to make the next action possible for someone who was not in the session.

## The Three Hard Blocks

Write `HANDOFF.md` only when one of these holds:

### 1. Missing access

A credential, permission, account, or external system is required, and no legitimate path from the environment provides it.

Examples: a sandbox API key that is not set; a private registry the agent cannot authenticate to; a production deploy role the agent does not hold.

Test: the command fails deterministically with an authentication or authorization error, and the value cannot be obtained from the repo, the environment, or an already-authorized session. "I would rather not try" is not a block.

### 2. Invalidating ambiguity

Two readings of the request produce incompatible deliverables, and choosing one would waste the other.

Examples: "export the customer data" where one reading includes PII and the other is anonymized by contract; "make it faster" where the target is latency in one reading and bundle size in another.

Test: you can name the two readings, the different artifacts they produce, and why evidence cannot pick one. A choice you can make, record as an assumption, and reverse later is not a block.

### 3. Budget spent

The iteration or wall-clock cap in `GOAL.md` is reached with red gates.

Test: the count is in `STATE.md` and matches the contract. Reaching the cap is not a reason to claim done; it is the reason to hand off with the remaining work and the next action.

## Not Blocks

These are work, and they belong in the loop:

- A failing test, a compile error, a flaky gate (one re-run, then treat it as red).
- A design choice with evidence on one side. Decide, record the decision, continue.
- A dependency conflict, a missing local tool, a version mismatch.
- An unfamiliar codebase, a large diff, a long test suite.
- A task the agent dislikes or finds tedious.
- "Should I commit / push / deploy?" when the goal implies it. The autonomy policy already answered.
- "Shall I continue?" Nothing in the goal is blocked.

Turning any of these into a handoff spends the user's attention on a decision the run was supposed to make.

## One Handoff

One file per goal. If a second block appears after the first is resolved, append a dated section to the same `HANDOFF.md`; do not open a new file per question.

Never drip questions into chat while a handoff is open. The file is the channel.

## Anatomy

```markdown
# Handoff: <slug>

- Date: <ISO 8601>
- Status: blocked
- Block kind: missing access | invalidating ambiguity | budget spent

## Done

- D1 — <state>; evidence: `EVIDENCE.md` <timestamp> / <gate>
- D2 — <state>; evidence: ...

## Remaining

- <task> — next action: `<exact command or edit>`
- <task> — next action: ...

## The block

<What cannot proceed, and why. One paragraph.>

```
<command>
<exact error, redacted>
```

## Options

1. **<option>** — <what it unblocks>. Cost: <time, money, risk>.
2. **<option>** — <what it unblocks>. Cost: <...>.
3. **Do nothing** — <consequence>. (Only when it is a real option.)

## Recommendation

Option <n> — <one sentence: why this one over the others>.

## To resume

1. <The exact value, decision, or permission the human must provide.>
2. Invoke goal-runner on `.goal/<slug>/`; it re-verifies <gate> and continues at `<next action>`.

## Do not

- <The tempting shortcut that would violate the contract or the autonomy policy.>
```

Every section earns its place:

- **Done** — evidence, so the human does not redo finished work. Use criterion IDs, not prose summaries.
- **Remaining** — the exact next action, so resuming is mechanical.
- **The block** — the command and the error. Without them the human cannot tell a missing key from a broken client.
- **Options** — real alternatives with cost and risk. A single option is a demand, not a decision.
- **Recommendation** — the agent has the most context; withholding a recommendation is abdicating it.
- **To resume** — what to provide and what happens next.
- **Do not** — the workaround that looks reasonable and violates the goal.

## Options That Are Actually Options

An option is a different way to unblock the goal, not a restatement of the same request.

Weak:

1. Give me the API key.
2. Don't do it.

Strong:

1. Provide a sandbox `EXCHANGE_API_KEY` — unblocks live verification of D3; cost: a few minutes; risk: none beyond normal sandbox use.
2. Point the test at the local mock server and amend D3 to contract-level verification — unblocks the run now; cost: the live integration stays unproven; risk: API drift goes undetected until the next real call.
3. Ship without the integration test and record it as a residual risk — unblocks delivery; cost: D3 stays unmet; risk: a broken sync reaches users.

The recommendation names the tradeoff: "Option 1, because it closes D3 with the least residual risk and the sandbox key is already issued."

## Resume After a Handoff

When the human provides what the block names:

1. Record the resolution in `STATE.md`: date, what was provided, and which blocker it clears.
2. If acceptance changed, add an amendment to `GOAL.md` with the user's decision and its reason.
3. Append a `## Resolution` section to `HANDOFF.md` with the date and the outcome. Do not edit the original block.
4. Re-run the gate that was blocked, fresh, and continue at the recorded next action.

On any later cold start, a dated `## Resolution` after the block means the block is cleared; do not stop on the old block. A handoff without a resolution is still open.

Never ask the same question twice. If the provided information is insufficient, say exactly what is still missing and why — once, in the same file.

## Secrets

Name the variable or the store, never the value:

- Good: "`EXCHANGE_API_KEY` is unset in the test environment."
- Bad: pasting a key the user sent into the handoff, evidence, or a command line.

If a value arrives in chat, use it through the environment or the secret store and keep it out of every file the skill writes. A credential committed to `.goal/` is a leak with a helpful filename.

## Example

```markdown
# Handoff: exchange-rate-sync

- Date: 2026-10-21T15:40:02Z
- Status: blocked
- Block kind: missing access

## Done

- D1 — Sync client handles success, 429, and network timeout; evidence: EVIDENCE.md 2026-10-21T14:12:08Z / G1
- D2 — Unit tests pass; evidence: EVIDENCE.md 2026-10-21T15:02:44Z / G2

## Remaining

- D3 — Run the sandbox integration test — next action: `python3 -m pytest tests/integration/test_sync.py -q` after exporting the key; done when G3 is green.
- D4 — Final full-suite pass — next action: `python3 -m pytest -q`; done when G4 is green.

## The block

The sandbox integration test requires `EXCHANGE_API_KEY`. It is not set, not in `.env.example`, and the repo has no other credential source.

```
python3 -m pytest tests/integration/test_sync.py -q
E   RuntimeError: EXCHANGE_API_KEY is not set
```

## Options

1. **Provide a sandbox key** — unblocks D3 and the final pass. Cost: minutes. Risk: normal sandbox use.
2. **Run against the local mock and amend D3** — unblocks the run now. Cost: live behavior stays unproven. Risk: API drift is caught only in production.

## Recommendation

Option 1 — it closes D3 with no residual risk, and the sandbox key is separate from production.

## To resume

1. Export a sandbox `EXCHANGE_API_KEY` in the shell that runs the tests.
2. Invoke goal-runner on `.goal/exchange-rate-sync/`; it re-verifies G3 and continues at the integration command.

## Do not

- Hardcode a key, disable the integration test, or mark D3 manual.
```
