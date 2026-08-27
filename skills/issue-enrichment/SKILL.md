---
name: issue-enrichment
description: "Use when a GitHub issue or feature request is too brief to implement and needs to be enriched with technical context from the codebase before implementation. Investigates the project, finds affected code, and rewrites the issue with the context a developer needs — without expanding scope."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, issues, enrichment, investigation, codebase-analysis, specification, triage]
    related_skills: [investigate-before-edit, codebase-audit]
---

# Issue Enrichment

## Overview

Many issues arrive as one-line descriptions that a developer cannot act on. This skill reads the issue, investigates the codebase to understand how the affected functionality works today, and rewrites the issue into a clear, actionable specification that preserves the original scope.

The deliverable is a rewritten issue body — readable by a person, not a technical audit. The skill is read-only with respect to source code: it searches, reads, traces, then produces enriched text.

## When to Use

- A GitHub issue or local task description is too brief or vague to implement.
- The user asks to "analyze and enrich", "add context to this issue", or "clarify this issue before implementing".
- Before handing an issue to a developer or coding agent who needs context to start.

Don't use for:
- Issues that already contain full context and acceptance criteria.
- Tasks that ask you to fix or implement the issue (use `investigate-before-edit`).
- Pure bug reproduction — investigate and debug it directly instead.

## Input

Accept the issue from one of these sources, in priority order:

1. **GitHub issue number** — `gh issue view N` (or the GitHub API / web page as a fallback).
2. **Issue URL** — fetch with `web_extract` or `gh issue view`.
3. **Local text** — pasted by the user or in a file path.

Record the original text verbatim before modifying anything — you will verify scope was preserved at the end.

### Read ALL comments (critical)

After recording the issue body, read every comment on the issue. Comments often contain:
- Additional requirements or scope refinements the original body doesn't mention.
- Bug reports, edge cases, or UX feedback from users/testers.
- Technical constraints or implementation notes from developers.
- Requests that contradict or supersede the original issue text.

Use `gh issue view N --comments` or fetch the issue page and extract comments. Treat each comment as a potential source of requirements — investigate them the same way you investigate the issue body. If a comment adds requirements, the enriched issue must represent them alongside the original text.

**Pitfall:** Skipping comments because the issue body "looks complete." The user will correct you — comments are part of the issue.

## Investigation (mandatory, before rewriting)

Read-only. No edits to source code. The goal: understand how the affected functionality works today so the enriched issue describes reality, not assumptions.

### 1. Restate the requirement

Parse the issue: what entity is affected, what action is requested, what should change. Write a one-sentence restatement in your own words. List the key terms to search for.

**Done when:** you have a concise restatement and a list of search terms.

### 2. Find the affected code

Read AGENTS.md / CLAUDE.md / .cursorrules / README / CONTEXT.md for project layout and conventions. Search the codebase for the key terms from step 1. Read the relevant files — do not guess from filenames.

**Actions:** `search_files(target='content')` for key terms; `read_file` on hits; `read_file` on project context docs.

**Done when:** the files directly related to the requirement are found and confirmed by reading.

### 3. Trace how it works today

Follow the data and execution flow through the affected code. For backend: request → view → serializer → model → response. For frontend: component → hook → API → render. Read each hop.

**Done when:** you can narrate the current behavior with `file:line` references.

### 4. Identify dependencies and edge cases

Note what the affected code depends on: other modules, external APIs, auth/permission rules, tenant isolation, configuration. Identify boundary conditions evident from the code: empty states, missing data, permission boundaries, pagination, timezones. Only include what the code or requirement shows — do not invent hypothetical scenarios.

**Done when:** dependencies, constraints, and real edge cases are recorded (or "none" is stated).

### 5. Check blast radius and tests

Search for all references to the symbols/files/components the issue touches. Find tests covering the area and the test command.

**Done when:** reference sites and test status are known.

## Parallel Investigation

When the issue spans independent areas (e.g. backend + frontend) and `delegate_task` is available, dispatch subagents per area. Each must return `file:line` evidence, not prose. Re-read critical files yourself before trusting subagent summaries.

## Writing the Enriched Issue

Rewrite the issue body. Every claim about current behavior must be backed by evidence you found. Omit any section if no relevant information was found — do not pad with generic content.

### Output Format

Keep it simple. This is a well-written issue, not a report:

```markdown
## Objective

<One or two sentences. What the issue asks for, in plain language. Preserves original scope.>

## Context

<How the affected functionality works today and why the change is needed. Written in plain prose, not bullet lists. Cite file paths inline like `module/views.py:142` so the developer knows where to look. 2-4 short paragraphs maximum.>

## Requested change

<What needs to change, in precise technical terms grounded in the code. The delta between current and desired behavior — not a solution design.>

## Acceptance criteria

- [ ] <Only if clearly inferable from the original requirement + code evidence.>
- [ ] <If none can be clearly inferred, omit this entire section.>
```

That's it. Four sections at most. If a section adds no value, leave it out.

### Language

Write the enriched issue — text AND section headings — in the user's language and the project's domain language. The template above shows English headings; translate them to match the output language (e.g., a Spanish-language issue uses `Objetivo`, `Contexto`, `Cambio solicitado`, `Criterios de aceptación`). If the project uses Spanish domain terms (e.g. IglesiaApp), use them. If the user writes in Spanish, output in Spanish.

### Scope Discipline (critical)

The enriched issue must NOT:

- Invent requirements not in the original.
- Expand scope (no "while we're at it" additions, no new features).
- Propose refactorings the issue didn't ask for.
- Assume behaviors that don't exist in the code — if you couldn't find it, don't guess.
- Be excessively long — aim for the minimum that makes the issue actionable. If it exceeds ~600 words, it probably has padding.

The enriched issue MUST:

- Preserve every requirement from the original issue.
- Cite file paths for claims about current behavior.
- Read like a person wrote it, not like a machine-generated audit.

## Delivery

1. Show the enriched issue to the user for review.
2. If the user approves, update GitHub with `gh issue edit N --body "..."` (or the GitHub API as a fallback).
3. If local, write to a file or display, as the user prefers.

Do not push to GitHub without user confirmation.

## Common Pitfalls

1. **Inventing context.** If `search_files` and `read_file` didn't surface it, it doesn't go in the issue. Don't guess.

2. **Expanding scope.** The investigation reveals adjacent functionality and the enriched issue starts describing changes the original never asked for. Cut anything the original didn't request.

3. **Padding with generic content.** "El código debe seguir las buenas prácticas" ("the code should follow good practices") is noise. Every sentence must carry specific information from the investigation.

4. **Making it read like a report.** The output is an issue a developer reads and understands quickly. If it reads like a technical audit document, simplify. Plain prose, short paragraphs, only what helps implementation.

5. **Acceptance criteria that are actually new requirements.** Criteria must be testable assertions derivable from the original requirement. If a criterion adds a constraint the issue didn't mention, remove it.

6. **Skipping investigation because the issue "looks obvious."** Brief issues need investigation the most — the implementer has the least context.

7. **Overwriting GitHub without confirmation.** Always show the enriched version first.

8. **Skipping issue comments.** The issue body is not the full picture — comments often contain additional requirements, UX feedback, or scope refinements. Always read all comments before investigating. The user will correct you if you miss them.

## Verification Checklist

- [ ] Investigation complete: affected code found, current behavior traced with file references
- [ ] All issue comments read and their requirements represented in the enriched version
- [ ] Original text preserved; every original requirement represented in enriched version
- [ ] No invented requirements, no scope expansion, no unrequested refactorings
- [ ] Every claim about current behavior backed by file path evidence
- [ ] Acceptance criteria only included when clearly inferable — otherwise omitted
- [ ] Reads like a well-written issue, not a technical audit
- [ ] Domain language matches project; output matches user's language
- [ ] Under ~600 words (no padding)
- [ ] Shown to user; GitHub update pending confirmation