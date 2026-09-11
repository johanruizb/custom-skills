---
name: anglicize-repo
description: |
  Translate a repository fully to English. Use when the user asks to anglicize a
  repo, translate it to English, or unify files that mix another language with
  English. Covers prose, comments, identifiers, and file names.
license: MIT
allowed-tools: Read, Glob, Grep, Edit, Write, Bash(git:*), Bash(rg:*)
---

# anglicize-repo

Unify a repository into English in one ordered pass: glossary first, prose second, identifiers last. The glossary carries the whole job. Translating file by file without one leaves the same source term as three different English words across the repo.

## Scope

Default to the full job: prose, comments, identifiers, file and directory names. If the user asks only for docs or prose, stop after the prose pass and say the identifier pass remains. Git history stays as it is; old commit messages are never rewritten.

## Steps

1. **Inventory.** Walk the tracked files and classify each as `translate`, `preserve`, or `mixed`. Check markdown, comments, docstrings, identifier names, CLI strings, and directory names. Done when every tracked file has one classification and every `translate` or `mixed` file lists the foreign-language content it holds.
2. **Glossary.** Collect the recurring domain nouns from the inventory and fix one English equivalent per term in a working note at the repo root. Done when every recurring term has exactly one entry. Get the user's sign-off on the glossary before touching any file.
3. **Prose pass.** Translate docs, comments, and docstrings using the glossary. Code blocks, shell commands, and config values stay untouched. Done when the sweep in step 5 returns nothing in prose files.
4. **Identifier pass.** Rename non-English identifiers, file names, and directory names. Use the language's rename tooling when it exists; otherwise search-and-replace and update every reference. Then run the project's tests and linters. Done when the suite is green.
5. **Sweep.** Grep the repo for every glossary source term and every foreign term found in the inventory. Done when each remaining hit sits in a `preserve` file. Report the files changed and the test result.

## Preserve list

Leave these alone even when they carry the foreign language:

- Strings that tests, fixtures, or snapshots compare against; changing them changes what the test asserts.
- Wire formats: API paths, protocol fields, serialized keys, log codes consumed elsewhere.
- Locale and i18n files; they are translations by definition.
- Licenses, attributions, quoted material, and proper nouns.
- Language keywords and standard library names.

To override a preserve-list hit, name the file and the consumer you checked first.

## Commits

Commit only on explicit request, one commit per pass (prose, identifiers) so each pass reverts on its own.