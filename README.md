# custom-skills

Personal collection of Claude Code skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Skills

### git-commit

Standardized git commits using Conventional Commits with autonomous message generation. A bash script handles mechanical data collection (diff, status, log, secret detection, type hints); the LLM handles semantic decisions (grouping, type, message).

Auto-detects commit type and scope from changes, commits autonomously without confirmation prompts, and splits changes into atomic commits grouped by logical type/scope. Operates on the current working directory.

**Structure:**

- `SKILL.md` — Workflow rules and safety protocol
- `scripts/prepare_commit.sh` — Data collection (diff, status, log, secret scan, type hints)
- `references/conventional-commits.md` — Type table, format, breaking changes reference

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit
```

**Usage:** Run the skill from Claude Code's command input. It will run the data collection script, analyze the output, group changes into atomic commits, and commit each group with a conventional commit message.

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
