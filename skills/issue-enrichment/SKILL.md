---
name: issue-enrichment
description: "Use when a GitHub issue or feature request is too brief to implement. Investigates the codebase and rewrites the issue with the technical context a developer needs, preserving the original scope."
license: MIT
metadata:
  author: Hermes Agent
  version: "1.3.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [github, issues, enrichment, investigation, codebase-analysis, specification, triage]
    related_skills: [investigate-before-edit, codebase-audit]
---

# Issue Enrichment

## Overview

Many issues arrive as one-line descriptions a developer cannot act on. This skill reads the issue and its comments, investigates how the affected functionality works today, and rewrites the issue into a spec a developer can start from, preserving the original scope. The deliverable is the rewritten issue body, an issue a person reads and understands quickly. Source code stays read-only. Search, read, trace, then write the text.

## When to Use

- A GitHub issue or local task description is too brief or vague to implement.
- The user asks to "analyze and enrich" an issue, "add context to this issue", or "clarify this issue before implementing".
- Before handing an issue to a developer or coding agent who needs context to start.

Don't use for:

- Issues that already carry full context and acceptance criteria.
- Implementation work (use `investigate-before-edit`).
- Pure bug reproduction. Debug it directly instead.

## Input

Take the issue from one of these sources, in priority order:

1. **GitHub issue number**: `gh issue view N --comments`, falling back to the GitHub API or the web page.
2. **Issue URL**: open the page or `gh issue view`.
3. **Local text**: pasted by the user or read from a file path.

Keep the original text verbatim. The enriched version must represent every requirement it carries.

### Read every comment

The body is rarely the whole issue. Comments carry additional requirements and scope refinements, bug reports and edge cases from users or testers, technical constraints from developers, and requests that contradict or supersede the body. Treat each comment as a requirement source: whatever a comment adds, the enriched issue represents it alongside the original text.

### Preserve screenshots

The body and the comments often carry screenshots: a bug state, a mockup, a reference screen. Read the image when the harness can view images, downloading it first if the URL alone does not render. A picture usually states the requirement more precisely than the text around it.

When a screenshot supports a requirement, carry it into the enriched issue:

- Keep its markdown reference, `![...](url)`, in the section it supports, so the implementer sees the same picture.
- Add one line describing the interface it shows: the screen, the state, the expected change (for example, "Payment modal today has no NIT field; the change adds it"). That description is what survives when the link breaks or the reader cannot open it.
- If the image cannot be viewed, keep the link and say next to it what could not be verified. Never drop it silently.

## Investigation (mandatory, before rewriting)

Read-only: search, read, trace. The goal is to describe how the affected functionality works today, so the enriched issue states reality instead of assumptions. A brief issue needs this phase most: the implementer starts with the least context.

### 1. Restate the requirement

Parse the issue and its comments: which entity is affected, what action is requested, what should change. Write a one-sentence restatement in your own words and list the terms to search for.

**Completion criterion:** the restatement names the entity, the action, and the expected change; the search terms are listed.

### 2. Find the affected code

Read the project context docs (AGENTS.md, CLAUDE.md, .cursorrules, README, CONTEXT.md) for layout and conventions. Search for the terms from step 1, then open every relevant hit and read it.

**Completion criterion:** the files directly related to the requirement are found and confirmed by reading.

### 3. Trace how it works today

Follow the data and execution flow through the affected code. Backend: request, view, serializer, model, response. Frontend: component, hook, API, render. Read each hop.

**Completion criterion:** you can narrate the current behavior with `file:line` references.

### 4. Dependencies and edge cases

Record what the affected code depends on: other modules, external APIs, auth and permission rules, tenant isolation, configuration. Record the boundary conditions evident in the code: empty states, missing data, permission boundaries, pagination, timezones. Include only what the code or the requirement shows.

**Completion criterion:** dependencies, constraints, and real edge cases are recorded, or "none" is stated.

### 5. Blast radius and tests

Search for every reference to the symbols, files, and components the issue touches. Find the tests covering the area and the command that runs them.

**Completion criterion:** every reference site is listed; the test command is known or the coverage gap is recorded.

### Parallel investigation

When the issue spans independent areas (say, backend and frontend) and the harness can dispatch subagents, send one per area. Each returns `file:line` evidence, not prose. Re-read the critical files yourself before trusting a summary.

## Writing the Enriched Issue

Rewrite the issue body. Every claim about current behavior cites the `file:line` where you saw it. Omit any section that found no relevant information, and never pad with generic content.

### Output Format

```markdown
## Objective

<One or two sentences: what the issue asks for, in plain language, original scope preserved.>

## Context

<How the affected functionality works today and why the change is needed, in plain prose rather than bullet lists. Cite paths inline like `module/views.py:142`. Two to four short paragraphs maximum.>

## Requested change

<The delta between current and desired behavior, in precise technical terms grounded in the code. Not a solution design.>

## Acceptance criteria

- [ ] <Testable assertions derived from the original requirement and the code evidence.>
- [ ] <If none can be derived, omit this entire section.>
```

Each preserved screenshot sits in the section it supports, with its markdown link and its one-line interface description.

### Rules

- **Scope.** Represent every requirement from the body and the comments. The enriched issue adds nothing else: no requirements the issue never asked for, no "while we're at it" refactors, no claim about current behavior you did not ground in the code.
- **Language.** Write the text and the headings in the user's language and the project's domain terms. A Spanish issue gets `Objetivo`, `Contexto`, `Cambio solicitado`, `Criterios de aceptación`.
- **Length.** The minimum that makes the issue actionable. Past roughly 600 words it has padding: every sentence carries specific information from the investigation.
- **Voice.** Write it as an issue for a person: plain prose, short paragraphs, no audit-report tone.

**Completion criterion:** every requirement from the original text and the comments is represented; every behavioral claim cites evidence; preserved screenshots keep their description; nothing goes beyond what the investigation found.

## Delivery

1. Show the enriched issue to the user for review.
2. On approval, update GitHub with `gh issue edit N --body "..."` (or the API as a fallback), or write the file locally.
3. Do not touch the issue before the user confirms.

## Common Pitfalls

1. **Inventing context.** If searching and reading did not surface it, it does not go in the issue. Every claim about current behavior needs a `file:line` you actually saw.
2. **Expanding scope.** Investigation reveals adjacent functionality and the draft starts describing changes the original never asked for. Cut anything the body and comments did not request.
3. **Padding with generic content.** "The code should follow good practices" is noise. Every sentence carries specific information from the investigation.
4. **Writing a report instead of an issue.** The output is read once, quickly, by someone about to implement. If it reads like a technical audit, simplify it.
5. **Acceptance criteria that are new requirements.** A criterion must be a testable assertion derived from the original request. One that adds a constraint the issue never mentioned is scope expansion in disguise.
6. **Skipping investigation because the issue "looks obvious."** A brief issue needs it most: the implementer starts with the least context.
7. **Overwriting GitHub before review.** Show the enriched version first; edit the issue only after the user confirms.
8. **Dropping comments or their screenshots.** The body is rarely the whole picture. Comments carry requirements, and a screenshot carries UI detail no text conveys. Read both and represent both.

## Verification Checklist

- [ ] Investigation complete: affected code found, current behavior traced with `file:line` references
- [ ] Every comment read, screenshots included, and its requirements represented in the enriched version
- [ ] Every original requirement represented; nothing invented, no scope expanded, no unrequested refactorings
- [ ] Every claim about current behavior backed by a `file:line` you read
- [ ] Acceptance criteria testable and derived from the original request, or the section omitted
- [ ] Preserved screenshots keep their link and their one-line interface description
- [ ] Output in the user's language, headings included, with the project's domain terms
- [ ] Reads like a well-written issue, not a technical audit
- [ ] Under roughly 600 words (no padding)
- [ ] Shown to the user; GitHub update pending confirmation
