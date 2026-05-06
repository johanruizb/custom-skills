# custom-skills

Personal collection of Claude Code skills, installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/johanruizb/custom-skills)](https://skills.sh/johanruizb/custom-skills)

## Skills

### git-commit

Standardized git commits using Conventional Commits specification with intelligent diff analysis and message generation.

Auto-detects commit type and scope from staged changes, generates messages in proper format, and follows git safety best practices.

**Install:**

```bash
npx skills add johanruizb/custom-skills --skill git-commit
```

**Usage:** Run the skill from Claude Code's command input. It will analyze your staged changes, suggest a conventional commit message, and guide you through the commit process.

## Requirements

- Node.js >= 18 (for `npx skills`)
- Git

## Credits

- [github/awesome-copilot](https://github.com/github/awesome-copilot) — original git-commit skill (MIT)
