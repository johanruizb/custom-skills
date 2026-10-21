# custom-skills

Personal collection of coding-agent skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Install all skills

```bash
npx skills add johanruizb/custom-skills --global
```

Each skill can also be installed on its own; the command is listed under every entry below.

## Skills

### git-commit

Fast, autonomous Conventional Commits built around the Git index and the current task context. Plain Git commands with commit invariants covering zero extra execution, safe staging, message validation, and safety stops.

Commits the existing staged set as authoritative. When nothing is staged, it stages only the explicit paths changed for the task. It creates one cohesive commit by default and splits only genuinely independent changes.

Every user-facing commit (`feat`, `fix`, `perf`, reverts, security) also extends the repo's existing changelog before the commit runs, so its entry rides inside the commit itself; entries follow Keep a Changelog 1.1.0 wherever the file's own format leaves it open, and the skill never creates the changelog. Commit conventions persist in `.commit/` at the repo root (`config.json` for machine values, `conventions.md` for the prose — gotchas and preferences the human corrected once), learned on the first run and reused by later ones; tool-generated changelogs (release-please, git-cliff) are left to their tools.

**Structure:**

- `SKILL.md`: Fast-path policy, `.commit/` state, changelog maintenance, cohesion rules, commit invariants, and safety boundaries
- `references/`: Optional type and breaking-change reference

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit --global
```

**Usage:** Explicitly ask Claude Code to commit the current changes. The skill reuses task context, inspects only when needed, and commits the staged set or explicit task paths without rereading the entire diff. On the first run it learns the repo's conventions into `.commit/`; from then on the changelog entry and the state refresh join the commit.

### code-documentation

Generate, update, or regenerate inline documentation (docstrings, JSDoc, comments) across a codebase. Analyzes project structure, detects language/framework conventions, offers incremental or full-regeneration modes, and validates that docs match the code without changing behavior.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill code-documentation --global
```

### code-health

Deep audit and cleanup of an entire codebase: performance, bugs, security, duplication, dead code, unnecessary abstractions, and accidental complexity. Reviews all source code (not just diffs), discovers available tools at runtime, adapts to any harness, uses a fixed question catalog, prioritizes findings by risk, and optionally applies and validates selected fixes in an isolated git worktree on a dedicated `code-health/audit-<mode>-<timestamp>` branch. Merged from the former `codebase-audit` and `simplify-codebase` skills.

**Structure:**

- `SKILL.md`: Core methodology (discovery, planning, audit, consolidation, worktree isolation, fix application, validation, reporting) and subagent strategy
- `references/`: Harness adapters, analysis checklists, finding schema, canonical user questions, and HTML report guide
- `scripts/`: Duplicate detection (`detect-duplicates.py`) and standalone HTML report generation (`generate-html-report.py`)

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill code-health --global
```

**Usage:** Ask the agent to audit, review, or find bugs, security issues, or performance bottlenecks in a codebase, or to simplify and deduplicate code. The skill maps modules, researches version-specific risks, and produces a structured report before prompting for which fixes to apply. Setup and fix selection use a fixed question catalog, so the same decision offers the same options on every run. Authorized fixes are applied in a dedicated worktree on a recognizable `code-health/audit-<mode>-<timestamp>` branch, leaving your checked-out branch untouched.

### goal-runner

Turn a request into a verifiable goal and drive it to completion without check-ins. Freezes a contract before any work — one goal sentence, observable done criteria, a runnable gate per criterion, no-goals, constraints, assumptions, and a budget — then loops plan → act → verify → record until every gate is green. State lives in `.goal/<slug>/` (contract, plan and next action, append-only evidence, optional handoff), so a new session resumes from the folder alone, re-runs the recorded gate fresh — every gate when the goal was marked done — and never asks the user to re-explain the goal. It hands off exactly once — on missing access, an invalidating ambiguity, or a spent budget — with options and a recommendation, and it never marks a gate green from memory, weakens a gate to pass, or closes a turn asking whether to continue.

**Structure:**

- `SKILL.md`: Goal contract, gate proof, autonomous loop, cold start, handoff rules, and anti-false-done checks
- `references/`: Contract authoring, loop mechanics and no-progress guards, handoff anatomy, harness adapters
- `templates/`: `GOAL.md`, `STATE.md`, and `HANDOFF.md`

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill goal-runner --global
```

**Usage:** Ask for a goal ("keep going until it's done") or point the agent at an existing `.goal/<slug>/` folder. The first run writes and freezes the contract, proves the gates can fail, and works the loop; later runs resume from the state files. The final report maps every criterion to its gate, command output, and evidence line, with residual risks called out.

### release-to-github

Cut a standardized release for any repository. A survey step reads each project's conventions first (version file, changelog, tag style, publish target, release tooling), so the same skill fits every project without per-repo configuration.

Derives the next version from the commits since the last tag (Conventional Commits → SemVer, with `0.x` handling), writes a Keep a Changelog section phrased for users instead of committers, and ends with a full-changelog comparison link plus a release commit, annotated tag, and a version branch (`release/vX.Y.Z`) for backporting fixes. Changelog entries use plain, specific language and go through the unslop skill when it is available. The irreversible steps (push, GitHub release, package publish) run last, after the release notes have been reviewed.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill release-to-github --global
```

**Usage:** Invoke `/release-to-github` in the project you want to release. Approve the proposed version, review the changelog section, and approve each publish step.

### prompt-enhancer

Rewrite and improve prompts to make them clear, actionable, and useful for ChatGPT, coding agents, design tools, product analysis, or any AI. Turns vague ideas, quick notes, or poorly written prompts into well-structured, ready-to-use instructions while preserving the original intent and technical terms.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill prompt-enhancer --global
```

### screaming-architecture-refactor

Reorganize a specific subpath of a project to Screaming Architecture + feature-based folders. Designed to run repeatedly over different paths of the same project for incremental, consistent, and safe migration.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill screaming-architecture-refactor --global
```

### web-perf-tuning

Restore fluidity to a web app that feels slow, heavy, or janky in normal use. For mature apps of any stack: records a measured baseline first, classifies findings into three layers (load, main thread, render churn), fixes one dominant bottleneck per lap using per-stack playbooks (React/Next, Vue/Nuxt, Angular, Svelte, vanilla), and verifies every fix with before/after numbers, reverting anything that doesn't measurably improve.

**Structure:**

- `SKILL.md`: The three layers, the lap method (orient → baseline → diagnose → fix → verify), the ledger report format
- `references/<stack>.md`: One playbook per stack: profiling recipes, static code sweeps, ranked bottlenecks. `references/vanilla.md` also holds the DOM/CSS layer shared by all stacks

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill web-perf-tuning --global
```

### anglicize-repo

Translate a repository fully to English in one ordered pass: a glossary of domain terms fixed before any edit, then prose, then identifiers and file names, ending with a grep sweep and a test run. A preserve list keeps tests, wire formats, and locale files untouched. Use on repos that mix another language with English.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill anglicize-repo --global
```

**Usage:** Ask for the full translation or scope it to prose only. The glossary gets reviewed before any file changes, and the identifier pass runs the test suite before the skill reports done.

### visual-feedback-loop

Force the agent to actually look at what it changed instead of assuming it matches the request. When the user provides a screenshot, mockup, or reference URL, describes a target look in words, or the change touches anything visible (UI, styling, charts, reports, PDFs, generated images), the skill runs a closed loop: write a visual contract from the reference, capture the real output at every named state, compare side by side, and close every delta — with evidence — before reporting done. Loop state persists in the project's `.feedback/` folder (app capture recipe, contract, captures, deltas), so a later run resumes instead of starting over. It adapts to the harness at runtime and refuses to claim a visual match when it cannot see.

**Structure:**

- `SKILL.md`: The loop (contract → capture → compare → fix), the resumable `.feedback/` state, the delta list, stop rules, and the pitfalls that produce false greens

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill visual-feedback-loop --global
```

**Usage:** Give the agent a reference (image, URL, or description) with your request. The agent builds a visual contract, shows the final capture next to the reference, and reports the closed delta list instead of "should look like you asked". Re-invoking it later resumes from `.feedback/`, reusing the app's capture recipe and the open deltas.

### fork-pr

Sync a fork's branch to its upstream parent in one pass. Pushes the branch to origin first (with confirmation around force pushes), then opens a PR in the original repo — or refreshes the existing one — regenerating its Conventional Commits title, its body (What / Changes / Badges / compare link), and one CI badge per workflow on the synced branch from the current state on every run.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill fork-pr --global
```

**Usage:** Run it inside the fork's checkout. The agent verifies the parent repo, resolves the base branch, pushes, and shows the drafted title and body before creating; later runs refresh the same PR in place instead of opening duplicates.

## Requirements

- Node.js >= 18 (for `npx skills`)
- Git

## Credits

- [github/awesome-copilot](https://github.com/github/awesome-copilot): original git-commit skill (MIT)
- [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode): inspiration for custom skills workflows (MIT)
