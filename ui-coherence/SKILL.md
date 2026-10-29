---
name: ui-coherence
description: "Use when the app's screens must read as one product: auditing visual consistency across every screen, unifying duplicated components or tokens, improving one screen without breaking the rest, or resuming the persisted improvement cycle in `.ui/`. Triggers: 'unifica la interfaz', 'audita la coherencia visual', 'que todas las pantallas se vean del mismo sistema', 'sigue el ciclo de diseño', 'revisa todas las pantallas'."
license: MIT
metadata:
  author: johanruizb, OpenCode
  version: "1.0.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [design-system, ui-consistency, audit, refactor, visual-validation, state-persistence, harness-agnostic]
    related_skills: [visual-feedback-loop, goal-runner, code-health]
---

# UI Coherence

## Overview

A screen can look right alone and still reveal that three sessions built the app. Coherence is a property of the **set**: the same spacing scale, type roles, component vocabulary, density rules, and interaction states across every screen, with differences that answer a functional need instead of an accident.

This skill keeps that property alive across sessions. It records the design system's source of truth, the screen/component inventory, and a prioritized backlog in `.ui/`, then runs the same loop every time:

```
load → inventory → audit → prioritize → implement (shared first) → validate → persist
```

**Iron law:**

```
The system is the default; every departure is recorded.
```

A difference with no record is drift. A recorded difference is a decision. The audit turns every difference into one or the other — never into uniformity.

## When to Use

- The user asks whether the app looks like one product, or asks for a UI consistency audit across screens.
- Two screens solve the same kind of job with different spacing, type, components, density, or states.
- Duplicated components or one-off styles need consolidation into shared tokens/components.
- One screen is being changed and must keep fitting the rest.
- The user asks to continue the improvement cycle (`.ui/` state exists).

Don't use when:

- The task is fidelity to one reference image or mockup. Use `visual-feedback-loop`.
- The task is judging whether the visual direction is good. Use `impeccable` or `design-taste-frontend`; this skill enforces *the project's* system, not taste.
- The change has no visual surface.

## The Decision Procedure

Apply this to every difference found:

1. **Different job?** A summary screen and a diagnostic console may need different density. If the difference answers a different job, it is a **justified deviation**: record it in the design source's deviations registry.
2. **Existing rule or component?** If a token, variant, or shared component already does the job, the difference is **accidental**: fix the screen, not the system.
3. **No rule exists?** It is a **system gap**: decide the rule, record it in the design source with its reason and consumers, then apply it everywhere. Changing screens before the rule exists creates the next drift.
4. **All screens agree, the source disagrees?** The source is stale, not the app. Update the design source in one coordinated change; do not mass-edit screens to match a document that drifted.

Uniformity is not the target. Screens with different jobs may look different; they may not look built by different teams.

## State: `.ui/`

Two committed files at the project root hold everything that must survive the session:

```
.ui/
  state.md     # design source, inventory, mode/cycle, next action
  backlog.md   # findings, decisions, closed items
```

- **Committed**, unlike `.feedback/` captures (ephemeral evidence, gitignored). A new session, model, or teammate must be able to resume.
- **Adopt, don't duplicate.** If the project already has a design source — `DESIGN.md`, design tokens, a Tailwind theme, CSS custom properties, a component library — point at it and read it. `.ui/` stores the pointer and the state, never a second copy of the tokens. If no source exists, create one from `templates/design-system.md` and record its path.
- **The inventory is a cache.** Stamp it with the commit and date it was built. Rebuild only when screens or shared components changed since; a stale inventory is worse than none.
- Write after every phase, not at the end. `Next action` must be executable by a cold start with no conversation history.

Templates: `templates/ui-state.md`, `templates/ui-backlog.md`.

## Findings

One line per difference, in `.ui/backlog.md`:

```
C-01 | screen:Tools | density | panel padding 12px, siblings 16px (rule S-2) | accidental | high | open
```

Fields: `id | scope | dimension | observed vs rule | class | severity | status`.

- **class**: `justified` | `accidental` | `system-gap`
- **severity**: `high` (breaks recognition or usability) | `medium` (visible drift) | `low` (cosmetic)
- **status**: `open` | `fixed` | `accepted` (deviation approved and registered) | `dropped` (rejected, reason recorded)

The backlog is the unit of work: one finding, one change set, one validation.

## Modes

The mode sets the **scope**, not the process. All modes run the same phases.

| Mode | Enters when | Ends when |
|---|---|---|
| `audit` | first run, "audit the app", "revisa todas las pantallas" | backlog written; no code touched |
| `screen` | a named screen | that screen and the consumers of any shared component it changes are validated |
| `unify` | duplicated patterns, "unifica la interfaz" | the shared token/component is consolidated and every consumer validated |
| `cycle` | "sigue el ciclo", autonomy requested | the delegated goal contract is met or a stop criterion fires |

Select the mode in Phase 0 and record it in `.ui/state.md`. An ambiguous request starts in `audit`: no code changes until the evaluation is done.

## Composition

Reach for another skill only when its job starts; never copy its internals.

- `visual-feedback-loop` — the capture/compare/close lap for Phase 5, one task per affected screen. It owns the capture recipe, `.feedback/`, and the green bar.
- `goal-runner` — only in `cycle` mode: freeze the backlog item as a verifiable goal with a budget and stop criteria in `.goal/`. Without it, `cycle` degrades to repeated `screen`/`unify` runs driven by the user.
- `code-health` — when duplication is structural (three copies of a component, not three styles), let it map the code; the visual decision stays here.

## Harness Adaptation

Map capabilities before starting; never substitute a guess for a check.

| Capability | Preferred | Fallback |
|---|---|---|
| Read/write project files | file tools | shell |
| Enumerate screens, components, tokens | file search + repo structure | ask the user |
| Run the app | shell (dev server / build) | ask the user for a running URL |
| Capture a screen | `visual-feedback-loop` recipe | Playwright / headless browser |
| See captures | multimodal file read | numeric checks (`getComputedStyle`, `getBoundingClientRect`), labeled *measured, not seen* |
| Structured questions | ask tool | numbered options in conversation |

If a capability is missing, record it in `.ui/state.md` and never claim an audit or validation the harness cannot support.

## Phase 0: Load State & Scope

1. Find the project root and read `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, and the design source (`DESIGN.md`, theme/token files).
2. Read `.ui/state.md` and `.ui/backlog.md` if present. If a cycle is open, confirm it and resume at its `Next action`; do not re-audit what is already recorded.
3. Select the mode and scope: the screens, components, and tokens this run covers.
4. Verify the inventory stamp against the current commit and the UI paths that changed since; mark it stale if screens or shared components moved.

**Completion criterion:** mode, scope, design-source path, inventory freshness, and the concrete next action are written in `.ui/state.md`; on resume, the user confirmed the cycle.

## Phase 1: Inventory

Enumerate, scoped to the mode:

- **Screens** — routes, windows, or views reachable from the app's navigation. Record each screen's *job* (summary, diagnostic, configuration, onboarding…) — job is what makes a difference justified.
- **Shared components** — every component used by more than one screen, with its consumers. Consumers are what a shared edit must revalidate.
- **Tokens** — spacing, type, color roles, radii, breakpoints. Record where they live, not what they should be.

Derive screens from the router or navigation manifest when one exists; otherwise walk the app's entry points. Never infer the screen list from folder names alone.

**Completion criterion:** every reachable route/window has a row in the inventory, every shared component lists its consumers (or `unused`), and the inventory is stamped with commit and date.

## Phase 2: Audit

Compare, scoped to the mode, across the dimensions in `references/audit-checklist.md`:

1. Spacing and rhythm
2. Type scale and roles
3. Color roles and semantic usage
4. Borders, radii, elevation
5. Density (padding, row heights, alignment)
6. Component duplication and divergent variants
7. Interaction states (hover, focus, disabled, loading, empty, error, success)

Compare each screen against the design source, and against siblings with the **same job**. A difference between a summary screen and a console is not evidence until the job is the same.

Classify every difference with the decision procedure and write one backlog line per difference. `audit` mode touches no code.

**Completion criterion:** every screen in scope is audited, and every difference has a line with class, severity, and status. "Looks consistent" is not a result; an empty backlog with a complete comparison is.

## Phase 3: Prioritize & Decide

1. Rank by severity, then by reach (how many screens or consumers the same fix would correct). Shared-first wins ties.
2. Pick one finding, or a small set sharing one root cause. "Improve everything" is not a scope.
3. For a **global change** (token, shared component, breakpoint, interaction pattern): list every affected screen and get approval before editing. Record the approval in the backlog.
4. For a **system gap**: write the rule into the design source first — value, reason, consumers — then implement.

**Completion criterion:** the selected finding has its fix, affected screens, validation plan, and approval if global; the design source covers every rule the fix relies on.

## Phase 4: Implement

1. Change the shared token/component first; then the screens.
2. A new value, variant, or component is a system change: record it in the design source with reason and consumers, or reuse what exists.
3. Keep the change set to the selected finding; note any forced deviation for Phase 5.

**Completion criterion:** the finding is implemented, no visual value exists outside the recorded system, and every new variant has a recorded reason and consumer list.

## Phase 5: Validate

1. For each affected screen, run the `visual-feedback-loop` lap: capture the real app in the states the change touches, compare against the design source and sibling screens, close every delta.
2. Revalidate every consumer of a shared component, not just the screen that motivated the change.
3. Run the project's functional checks (tests, type check, build) when the change can affect behavior.
4. Store captures in `.feedback/` and link them from `.ui/state.md`.

A capture you could not see is *measured evidence*, not a visual check. State which one it is.

**Completion criterion:** every affected screen is green or its surviving delta is recorded as an accepted deviation; functional checks pass or their failure is explained.

## Phase 6: Persist & Close

1. Update `.ui/backlog.md`: status, decision, reason, validation evidence.
2. Update `.ui/state.md`: cycle, closed findings, inventory stamp if the screen/component set changed, and the **next action** for a cold start.
3. Record global decisions in the project's ADR log if one exists; otherwise in the backlog's Decisions section.
4. Report: what changed, which screens were validated, what remains open, what could not be verified.

**Completion criterion:** a cold start can read `.ui/state.md` and execute the next action with no conversation history; every closed finding names its evidence.

## Stop Criteria

Stop and report when any holds:

- `audit`: the backlog is written and no code was touched.
- The backlog has no open `high`/`medium` finding in scope.
- The next finding needs a global change the user has not approved.
- The same finding survives three validation laps.
- The harness cannot run or capture the app; the limitation is recorded and the user decides.
- `cycle`: the `goal-runner` contract is met or its budget is exhausted.

Stopping with a recorded backlog is a valid outcome. Churning screens to show activity is not.

## Common Pitfalls

- **Coherence as uniformity.** Forcing a summary screen and a diagnostic console into the same density. Different job, different composition — same vocabulary.
- **Auditing taste instead of the system.** "I would have used more whitespace" is not a finding unless a recorded rule says so.
- **Trusting the inventory.** Screens and shared components change; a stale inventory sends the audit to the wrong places.
- **Counting rendering noise.** Antialiasing, subpixel differences, and viewport mismatches are not drift.
- **Fixing the screen before the rule.** The same gap reappears in the next screen the agent touches.
- **Mistaking a stale source for six accidents.** When every screen agrees with every other screen, the document is what drifted; fix it once.
- **Validating only the touched screen.** A shared token change reaches every consumer; so must the validation.
- **Declaring green from code.** Reading the diff cannot tell you how the app looks.
- **Unbounded unification.** A refactor that rewrites unrelated screens cannot be attributed or reverted.

## Verification Checklist

- [ ] `.ui/state.md` and `.ui/backlog.md` exist and are committed.
- [ ] The design source is discovered, not duplicated; `.ui/` points at it.
- [ ] Inventory covers every reachable screen and lists consumers per shared component.
- [ ] Every backlog line has class, severity, and status.
- [ ] Every departure from the system is recorded as a justified deviation; every unrecorded departure is fixed or backlogged.
- [ ] Shared components were changed before screens, and every consumer was validated.
- [ ] Affected screens have captures and a green result, or a recorded limitation.
- [ ] The next action is concrete enough for a cold start.
