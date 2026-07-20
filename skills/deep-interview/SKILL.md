---
name: deep-interview
description: |
  Run a structured Socratic requirements interview before planning or implementation. Use when the user has a vague idea, asks for a deep interview, says "interview me", "ask me questions", "do not assume", "make sure you understand", "no quiero que asumas", "entrevistame", or wants requirements clarified before code changes. Produces a scored specification with goals, constraints, non-goals, acceptance criteria, risks, open questions, and an explicit approval gate before execution.
license: MIT
---

# Deep Interview

## Overview

Use this skill to convert unclear intent into a concrete, approved specification before planning or implementation. Ask targeted questions, score clarity after each answer, and do not mutate files or start execution until the user explicitly approves the next path.

This skill is inspired by `deep-interview` from `Yeachan-Heo/oh-my-claudecode`, but it is portable: do not assume OMC-specific tools such as `AskUserQuestion`, `state_write`, or `Skill(...)` exist.

## Operating Rules

- Ask exactly one substantive question per round.
- Target the weakest clarity dimension, not the easiest topic.
- Before asking about an existing codebase, inspect the repository with available code-discovery tools and cite the evidence you found.
- Do not ask the user facts that the repo can answer.
- Score ambiguity after every answered round and show the score.
- Preserve scope across components; do not over-focus on the component with the most detail while ignoring siblings.
- Summarize oversized prompts, logs, transcripts, or file excerpts before scoring or generating the spec.
- Stop immediately if the user says to cancel or stop.
- Treat implementation, file mutation, commits, pushes, PRs, deploys, and execution-skill handoffs as blocked until explicit post-spec approval.

## Modes

Parse optional depth hints from the user's request:

| Mode | Use When | Target Ambiguity | Soft Limit | Hard Limit |
| --- | --- | ---: | ---: | ---: |
| `--quick` | User wants brief clarification before a small change | `<= 0.35` | 3 rounds | 5 rounds |
| `--standard` | Default for unclear but bounded work | `<= 0.20` | 6 rounds | 10 rounds |
| `--deep` | High-risk, broad, architectural, or product-defining work | `<= 0.10` | 10 rounds | 18 rounds |

Default to `--standard` when no mode is specified. If the user asks to proceed before the target is met, allow early exit only after warning about remaining gaps.

## Runtime Input

Use the richest interactive input available, but keep the one-question rule:

- If a structured question tool is available and allowed, ask one question per call with 2-3 options plus free-form fallback.
- If no structured tool is available, ask one plain-text question and wait.
- Do not batch multiple requirements questions into one turn.
- For final execution approval, present concise options and wait for an explicit selection.

## Workflow

### 1. Initialize

1. Restate the user's idea in one sentence.
2. Classify the task:
   - **Greenfield**: creating a new artifact, feature, system, workflow, document, or app.
   - **Brownfield**: modifying or extending an existing codebase, process, repository, PR, deployment, or documented system.
3. For brownfield tasks, gather repository facts before the first requirements question:
   - Prefer available graph or semantic code tools.
   - Use `rg`, file reads, tests, or project metadata when graph tools are unavailable or insufficient.
   - Summarize relevant files, symbols, routes, configs, tests, and prior planning artifacts with citations.
4. Normalize oversized context into a short working summary with explicit decisions, constraints, unknowns, file references, and non-goals.
5. Announce the mode, target ambiguity, and that execution is approval-gated.

### 2. Round 0: Topology Gate

Before scoring, confirm the top-level components so later questions do not collapse the scope.

Extract 1-6 components from the idea and repo context. Components are outcomes, surfaces, workflows, integrations, or deliverables that can succeed or fail independently.

Ask:

```text
Round 0 | Topology confirmation | Ambiguity: not scored yet

I read this as these top-level components:
1. {component}: {one-sentence description}
2. ...

Is this topology right? Should anything be added, removed, merged, split, or deferred?
```

After the answer, lock the topology as active and deferred components. Carry every active component into scoring and into the final spec.

### 3. Interview Loop

Repeat until ambiguity is at or below the target, the hard limit is reached, or the user exits early.

For each round:

1. Choose the active component and clarity dimension with the weakest score.
2. Rotate across similarly weak components so siblings get coverage.
3. Ask one question that exposes an assumption or closes a high-leverage gap.
4. After the answer, score clarity and report progress.
5. Store the Q&A, score, open gap, and next target in the working transcript.

Question styles by dimension:

| Dimension | Ask About | Example Shape |
| --- | --- | --- |
| Goal | What exactly changes or happens | "When you say X, what user action or system event starts it?" |
| Constraints | Boundaries, dependencies, non-goals, timing, cost, compliance | "What must this not do, support, or change?" |
| Success Criteria | Testable completion and validation | "What would make you say this is done and correct?" |
| Context | Existing code, architecture, data, workflows, ownership | "I found X in `{path}`. Should this extend that pattern or intentionally diverge?" |
| Ontology | Core nouns and relationships when the domain keeps shifting | "What is the core entity here, and what are merely views or supporting concepts?" |

Challenge the framing when useful:

- Round 4+: ask a contrarian question that tests a core assumption.
- Round 6+: ask a simplifier question that removes nonessential complexity.
- Round 8+ with ambiguity above `0.30`: ask an ontology question about what the thing fundamentally is.

### 4. Scoring

Score each dimension from `0.0` to `1.0` after every answered round.

Greenfield formula:

```text
ambiguity = 1 - (goal * 0.40 + constraints * 0.30 + criteria * 0.30)
```

Brownfield formula:

```text
ambiguity = 1 - (goal * 0.35 + constraints * 0.25 + criteria * 0.25 + context * 0.15)
```

When there are multiple active components, compute component-level scores first. The overall score should reflect the weakest meaningful coverage, not an average that hides an unclear component.

Report progress like this:

```text
Round {n} complete.

| Dimension | Score | Weight | Gap |
| --- | ---: | ---: | --- |
| Goal | {score} | {weight} | {gap or Clear} |
| Constraints | {score} | {weight} | {gap or Clear} |
| Success Criteria | {score} | {weight} | {gap or Clear} |
| Context | {score} | {weight} | {gap or Clear} |

Ambiguity: {percent}% (target: {target}%)
Topology: targeted {component}; active {count}; deferred {count}
Next target: {component} / {dimension} because {rationale}
```

Omit the Context row for greenfield tasks.

## Specification Output

When the target is met, the hard limit is reached, or the user chooses early exit, produce a spec before any execution.

If file writing is available, write the spec to:

```text
.deep-interview/specs/deep-interview-{slug}.md
```

If the target repository already uses `.omc/specs/`, use that path instead to match local convention. If file writing is not available, output the spec in the conversation.

Use this structure:

```markdown
# Deep Interview Spec: {Title}

## Metadata
- Status: pending approval
- Type: greenfield | brownfield
- Mode: quick | standard | deep
- Rounds: {count}
- Final Ambiguity: {percent}%
- Target Ambiguity: {percent}%
- Generated: {ISO timestamp}
- Spec Path: {path or inline}

## Goal
{One precise goal statement covering every active component.}

## Topology
| Component | Status | Description | Coverage / Deferral |
| --- | --- | --- | --- |
| {name} | active | {description} | {coverage note} |

## Requirements
- {requirement}

## Constraints
- {constraint}

## Non-Goals
- {explicitly excluded scope}

## Acceptance Criteria
- [ ] {testable criterion}

## Assumptions Exposed And Resolved
| Assumption | Questioned By | Resolution |
| --- | --- | --- |
| {assumption} | {round/question} | {decision} |

## Technical Context
{Brownfield repo findings with file/path/symbol citations, or greenfield technical choices and constraints.}

## Risks And Open Questions
- {risk or unresolved question}

## Interview Transcript
### Round 0
**Q:** {question}
**A:** {answer}

### Round 1
**Q:** {question}
**A:** {answer}
**Ambiguity:** {percent}%
```

## Approval Gate

After the spec is ready, stop and ask how to proceed. Do not execute by default.

Offer options appropriate to the runtime:

1. **Refine plan**: turn the spec into an implementation plan, then stop again for execution approval.
2. **Implement now**: proceed with the approved spec.
3. **Continue interview**: ask more questions to lower ambiguity.
4. **Stop here**: leave the spec as the artifact.

Only continue to planning or implementation after the user explicitly chooses that path.

## Quality Checklist

- Topology was confirmed before scoring.
- Every active component appears in the final spec.
- Brownfield questions cite repo evidence before asking for decisions.
- Each round asked one substantive question.
- Ambiguity was scored after every answered round.
- The weakest dimension and next target were named each round.
- The final spec includes goal, topology, requirements, constraints, non-goals, acceptance criteria, technical context, risks, open questions, and transcript.
- No mutation or execution happened before explicit approval.

## Credits

Inspired by `deep-interview` from [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode), licensed under MIT.
