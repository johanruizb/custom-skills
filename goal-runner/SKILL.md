---
name: goal-runner
description: "Turn a request into a verifiable goal and drive it to completion without check-ins. Use when the user says 'define una meta', 'hazlo autónomo', 'no me pidas confirmación', 'trabaja hasta terminarlo', 'sigue sin parar', 'goal', 'keep going', 'do not stop until done', or asks to resume a goal from `.goal/`. Freezes a contract with observable done criteria and a runnable gate per criterion, persists plan, progress, and append-only evidence in `.goal/<slug>/`, and lets a new session resume from disk without re-explaining anything."
license: MIT
metadata:
  author: johanruizb, OpenCode
  version: "0.1.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [goal-execution, autonomy, verification, gates, state-persistence, cold-start, handoff, harness-agnostic]
    related_skills: [unlazy]
---

# goal-runner

## Overview

A request like "add CSV export" usually ends with a confident summary and no proof. The gap is rarely effort; it is that done was never defined. This skill defines it before touching the work, then runs until the definition is met.

Three ideas carry the run:

- **Contract** — one goal sentence, observable done criteria, constraints, no-goals, assumptions, budget, and a **gate** per criterion.
- **Gate** — a binary check: an exact command and the output that means pass. A gate is *red* until a *fresh* run passes. Fresh means executed now, in this session, with the output captured. A previous pass is history, not evidence.
- **Lap** — one pass of the loop: plan → act → verify → record.

```
red gate → act → run gate fresh → green? → next red gate
                             └── no → record → next strategy
```

The loop and all of its state live on disk under `.goal/<slug>/` in the repository where the work happens. A cut turn, a context compaction, or a new session resumes from the last recorded state instead of from chat.

**Iron law:** no gate is green without a fresh run, and no goal is done with a red gate.

## When to Use

- The user turns a request into a goal to finish: *"define una meta"*, *"hazlo autónomo"*, *"no me pidas confirmación"*, *"trabaja hasta terminarlo"*, *"sigue sin parar"*, *"goal"*, *"keep going"*, *"do not stop until done"*.
- The work is multi-step and likely to outlive one turn or one context window.
- The user wants evidence that the result is done, not a summary that claims it.
- A previous goal run must resume: *"retoma la meta"*, *"sigue desde .goal/"*, *"continue the goal"*.

Don't use when:

- The task is a single edit, lookup, or factual answer; a contract costs more than the work.
- The outcome is open-ended exploration ("investigate X", "look around") with no end state that can be called done.
- Every step needs human judgment (design direction, negotiation, hiring); the loop would stall at the first decision.
- No observable outcome can be named, so no gate can exist.

## The `.goal/<slug>/` Folder

One folder per goal at the root of the repository being changed. The slug is kebab-case and short: `add-csv-export`.

| File | Role | Write rule |
|---|---|---|
| `GOAL.md` | The frozen contract: goal, done criteria, gates, no-goals, constraints, assumptions, budget, amendments. | Written before work; changed only through Amendments. |
| `STATE.md` | Live plan, gate status, iteration count, strategy, blockers, backlog, and the exact next action. | Rewritten after every lap and before any yield. |
| `EVIDENCE.md` | Append-only log: gate, command, cwd, exit code, output, timestamp. | Append only. Never edit or delete an entry. |
| `HANDOFF.md` | The single escalation: block, options, recommendation, resume steps. | Written only on a hard block. |

Track `.goal/` with the work or ignore it, following the repo's habit; either way it stays on disk until the goal closes. The contract and state are the interface between runs. If a cold start cannot act from them, they are incomplete.

Templates: `templates/GOAL.md`, `templates/STATE.md`, `templates/HANDOFF.md`. Authoring detail: `references/goal-contract.md`.

## Autonomy Policy

The goal authorizes the work it implies: read and write files, install dependencies, run commands and tests, commit, push, or deploy when those actions are part of reaching a green gate. Do not ask for approval for any of it.

The authority stops at four lines:

- Never invent, guess, or hardcode credentials, tokens, or keys.
- Never bypass authentication, authorization, or a safety check to make a gate pass.
- Never copy secrets into `GOAL.md`, `STATE.md`, `EVIDENCE.md`, or `HANDOFF.md`; name where the value lives and redact it.
- Never destroy or rewrite anything outside the goal's scope, including unrelated work in the repository.

Crossing one of these lines is a hard block, not a permission request: write the handoff.

## Phase 0 — Cold Start

Read `.goal/` before anything else.

**New goal** — no folder matches the request. Choose the slug and go to Phase 1.

**Existing goal** — the user named a slug, or exactly one goal is `draft`, `active`, `blocked`, or `done`: read `GOAL.md`, then `STATE.md`, then the tail of `EVIDENCE.md`.

- If `HANDOFF.md` exists, read it first. It is cleared when a `## Resolution` section follows the block or when the user supplies what the block names; otherwise present it and stop. On clearing, append the resolution to `HANDOFF.md` and `STATE.md`, then continue at the recorded next action.
- A `draft` goal resumes at Phase 1: finish and freeze the contract before acting.
- Re-run the last gate named in `STATE.md`. Do not trust its recorded status.
- Green → execute the recorded next action. Red → the next action is to repair it; record the fresh result before acting.
- If `GOAL.md` says `done`, resume as a **re-verification**: run every gate fresh. All green → confirm done with new evidence. Any red → set `Status: active`, record the failure, and repair. A done claim rots like any other.
- Never re-ask what `GOAL.md` already decided, and never rebuild the plan while `STATE.md` holds one.

If several goals are active and the request does not identify one, resume the most recently updated and say so. A handoff is for blocks, not for tidiness.

**Completion criterion:** you have named the goal, the fresh result that grounds the resume (the last gate, or all gates for a done goal), and the exact next action; `STATE.md` records the resume.

## Phase 1 — Draft the Contract

Create `.goal/<slug>/GOAL.md` from the template. The goal sentence names an outcome, not an activity:

- `Add CSV export of the filtered table, with a header row and RFC 4180 quoting.` — outcome, gateable.
- `Work on CSV export.` — activity, uncloseable.

For each done criterion `D1…Dn`:

- State the observable end state that a stranger could check.
- Pair it with at least one gate `G1…Gn`: exact command, working directory, expected exit code, and a decisive output token. Put the gate beside the criterion it proves.
- Prefer a gate that can fail. A command that prints `ok` unconditionally proves nothing.
- Use a manual gate only when no command can decide the outcome. Name the evidence, the judge, and why automation is impossible.

Fill no-goals, constraints, assumptions, and the budget: maximum laps and wall-clock. Record reversible assumptions instead of asking. A question becomes a handoff only when its answer changes the deliverable in incompatible ways.

For a goal with several independently deliverable outcomes, split it into subgoals with dependencies, leaf gates, and an integration gate — see `references/goal-contract.md`. A simple goal stays one contract; unnecessary depth is a second plan to maintain.

**Completion criterion:** every done criterion maps to at least one gate; every gate names a command, a cwd, and an expected result, or carries a written manual justification; no-goals and budget are filled.

## Phase 2 — Prove the Gates, Then Freeze

Run every gate once before doing the work, from its declared cwd, and append the result to `EVIDENCE.md`. This baseline is the only free pass: it shows whether a gate measures what it claims.

Check each gate for the common failures:

- It passes on an empty or placeholder implementation → it does not measure the criterion.
- It cannot fail: `true`, `echo`, `cmd || true`, or a pipeline that returns the last command's status (`cmd | tail` without `pipefail`).
- It measures a proxy (the file exists) where the criterion is behavior (the CLI prints the header).
- It depends on ambient state: network, a warm cache, an unset variable, a different shell.

Fix the gate, not the criterion. Then set `Status: frozen` and the freeze date in `GOAL.md`.

**Completion criterion:** every gate has a baseline result on record; every gate that was green before any work is either a genuinely pre-met criterion or rewritten; the contract is frozen.

## Phase 3 — Run the Loop

Each lap takes the single next action from `STATE.md` through four steps:

1. **Plan** — choose the action that closes the most urgent red gate.
2. **Act** — carry it out completely. No placeholders, no deferred halves.
3. **Verify** — run every gate the action could touch, fresh.
4. **Record** — append results to `EVIDENCE.md`; update `STATE.md` with gate status, iteration count, strategy, backlog, and the exact next action.

Then start the next lap without asking. The loop is the default state of the run. It exits in exactly two ways: all gates green, or a handoff — the budget-spent case included. Anything else is a stopped loop, not a finish.

Guards, detailed in `references/autonomy-loop.md`:

- **No-progress** — three consecutive laps with the same failure and no gate flipping green: change strategy, not wording. Name strategy A in `STATE.md`; when it fails, strategy B. Two exhausted strategies, or six laps on one failure: handoff.
- **Scope** — work not required by a done criterion and not blocking a gate goes to `Backlog` in `STATE.md`. It is not implemented silently and not dropped.
- **Budget** — count laps against the contract. Reaching the cap is a handoff, never a done claim.
- **Turn boundary** — if the harness ends the turn, `STATE.md` must already hold the last verified state and the exact next action. Never close with "shall I continue?" or a progress summary presented as a result.

**Completion criterion (per lap):** `EVIDENCE.md` holds the fresh result of every gate the lap touched, and `STATE.md` names the next action precisely enough for a cold start to execute it without chat history.

## Phase 4 — Claim Done

Done is a verification pass, not a decision.

1. Re-run every gate in `GOAL.md` from its declared cwd, in one pass, fresh. Append each result.
2. Reconcile: every done criterion has a gate, every gate is green, every green has an evidence line from this pass.
3. Check the boundaries: no-goals untouched, amendments dated and reasoned, backlog holds nothing a done criterion requires.
4. Report a table of criterion → gate → command → fresh result → evidence line, plus budget used, residual risks, and open backlog.

If any gate is red, missing, or backed only by older evidence, the goal is not done: return to Phase 3 with that gate as the next action.

**Completion criterion:** a reader can re-run each command from the report and reproduce the same pass; no claim lacks a line in `EVIDENCE.md` from this final pass.

## Phase 5 — Handoff

Write `HANDOFF.md` from the template only when one of three conditions holds:

- A credential, permission, or external access is missing and cannot be legitimately obtained from the environment.
- An ambiguity makes two incompatible deliverables possible, and choosing one would waste the other.
- The budget is spent with red gates.

Everything else is work: a failing test, a hard design choice with evidence on one side, a dependency that needs a different version. Decide, record the decision in `STATE.md`, and continue.

The handoff is one file, not a conversation: what is done with evidence, what remains with the exact next action, the exact block (command and error), at least two options with cost and risk, one recommendation, and what the human must provide to resume. Append a dated section if a later block appears; never open a second file per question.

After writing it, stop. Do not keep working around the block, and do not repeat the question in chat.

**Completion criterion:** someone who was not in the session can clear the block from the file alone and knows the first command to run afterwards.

## Common Pitfalls

- **A gate that cannot fail.** `echo ok`, `true`, `cmd || true`, or a pipeline without `pipefail` turns verification into theater.
- **Passing before the work.** A file-existence check or a stale artifact makes a red criterion look green. Baseline every gate and inspect what it actually measures.
- **Weakening a gate after it fails.** Lowering a threshold, deleting a failed check, or relabeling it manual is a false done with extra steps. A weaker acceptance is a goal change: hand off.
- **Evidence from memory.** "It passed earlier" is not evidence. Re-run at the final claim, every gate.
- **Recording at the end.** A crash or compaction then loses the run. Write `STATE.md` and `EVIDENCE.md` after every lap.
- **A vague next action.** "Continue with tests" cannot be resumed. Name the file, the command, and the observable result.
- **Asking permission at the first friction.** "Shall I continue?" breaks the one promise the user asked for. Continue, or hand off when the block is real.
- **Handoff as an escape hatch.** A hard test is not a block. Three failed attempts earn a strategy change, not a question.
- **Silent scope drift.** Implementing the backlog because it was nearby spends the run on work nobody asked for.
- **State kept in chat.** It dies with the context. The disk is the source of truth.

## Verification

Before reporting a goal complete, confirm all of these:

- [ ] `GOAL.md` is frozen, and every done criterion maps to at least one gate.
- [ ] Every gate names a command, cwd, and expected result; manual gates carry a written justification.
- [ ] Every green gate has an `EVIDENCE.md` line with a timestamp from the final pass.
- [ ] No gate was weakened, deleted, or converted to manual after failing.
- [ ] `STATE.md` holds the current iteration and an exact next action; no required work sits in Backlog.
- [ ] `HANDOFF.md` exists only for one of the three hard blocks and contains options plus a recommendation.
- [ ] The final report maps criterion → gate → command output → evidence, and lists residual risks.
- [ ] The turn did not end with a permission question or a partial summary presented as final.
