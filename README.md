# custom-skills

Personal collection of Claude Code skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Skills

### git-commit

Standardized git commits using Conventional Commits specification with intelligent diff analysis and autonomous message generation.

Auto-detects commit type and scope from staged changes, commits autonomously without confirmation prompts, and splits changes into atomic commits grouped by logical type/scope. Operates on the current working directory.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit
```

**Usage:** Run the skill from Claude Code's command input. It will analyze your staged changes, suggest a conventional commit message, and guide you through the commit process.

### pr-review

Reviews a Pull Request and updates its title and description with a structured Spanish summary (CodeRabbit-style) ready for human reviewers, applies standard GitHub labels, and coordinates Bug, Performance, and Security subagents that publish actionable review comments on the PR.

Does not modify source code or create commits; it analyzes the PR diff, edits title and description, applies labels, and posts inline or general review comments.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill pr-review
```

**Usage:** Run the skill from Claude Code's command input. It will analyze the PR diff, update the title and description in Spanish, apply relevant labels, and post validated review findings as comments on the PR.

### deep-interview

Structured Socratic requirements interview for vague ideas before planning or implementation.

Asks one targeted question at a time, scores ambiguity across weighted clarity dimensions, confirms the top-level scope, inspects brownfield code before asking repository questions, and produces a pending-approval specification before any execution.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill deep-interview
```

**Usage:** Run the skill when a request is vague or high-risk, for example "deep interview this feature idea", "interview me before coding", or "no quiero que asumas". It will clarify requirements and generate a spec before implementation.

## Requirements

- Node.js >= 18 (for `npx skills`)
- Git

## Credits

- [github/awesome-copilot](https://github.com/github/awesome-copilot) — original git-commit skill (MIT)
- [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — inspiration for deep-interview (MIT)
