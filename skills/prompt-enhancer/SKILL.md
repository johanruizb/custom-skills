---
name: prompt-enhancer
description: "Use when the user asks to improve, rewrite, or polish a prompt ('mejora este prompt', 'reescribe este prompt', 'hazlo más claro', 'pulir este prompt') or sends a raw idea, note, or rough draft to turn into a clear, actionable prompt. Transforms vague ideas into well-structured, ready-to-use prompts for any AI — ChatGPT, coding agents, design tools — preserving the original intent and technical terms."
version: 1.4.0
author: johanruizb, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prompts, rewriting, clarity, ai-assistance, communication]
    related_skills: []
---

# Prompt Enhancer Skill

Transforms raw ideas, quick notes, or poorly written prompts into clear, actionable, useful prompts for any AI. It does not change the original intent — it only improves clarity, structure, and precision. It does not do pure grammar fixes and does not translate prompts.

## When to Use

- User asks to "mejora este prompt", "reescribir prompt", "hacer más claro", "pulir prompt", or the English equivalents ("improve this prompt", "rewrite this prompt").
- User sends a raw idea, note, or rough draft and wants it turned into a usable prompt.
- User needs variations of a prompt (more direct, more technical, more detailed).

Don't use for:
- Pure grammar correction with no structural improvement.
- Translating prompts.
- Generating content that is not a prompt.

## Core Rules

Apply in order before generating any output:

1. **Understand the main intent.** Extract what the user wants to achieve. If the intent is ambiguous, choose the most probable interpretation and note it under Assumptions.

2. **Preserve meaning.** Do not invent requirements, do not add unrequested functionality, do not change the goal. What the user did not say, do not assume.

3. **Improve clarity and precision.** Remove ambiguity, redundant phrases, and detours. Every sentence must carry actionable information.

4. **Turn vague statements into concrete instructions.** "Hazlo bonito" ("make it pretty") → "Usa paleta monocromática con sombras sutiles, espaciado de 16px y tipografía sans-serif". "Que funcione bien" ("make it work well") → "Debe manejar hasta 1000 registros sin degradación, responder en <200ms y mostrar un estado de carga".

5. **Structure into sections when it helps.** For complex prompts: Objective, Context, Requirements, Constraints, Acceptance criteria, Deliverables. For simple prompts, a direct one-piece version is better.

6. **Adjust tone to context:**
   - **Software development:** technical, precise, with constraints, scope, and acceptance criteria.
   - **UI/UX:** visual consistency, hierarchy, spacing, alignment, interaction, coherence with the existing system.
   - **Analysis:** objectives, context, review steps, and expected deliverables.
   - **Creative/General:** natural, descriptive tone with room for interpretation.

7. **Don't overcomplicate.** If the original prompt is already clear in 3 lines, don't turn it into 20.

8. **Preserve technical terms.** Component names, paths, variables, IDs, URLs, commands — keep them exactly as the user wrote them.

9. **Resolve ambiguity with tools before delivering.** If important information is missing, add "Assumptions" at the end. If there are multiple reasonable interpretations and the ambiguity is critical (it changes the outcome significantly), use the `clarify` tool to ask the user before delivering. If `clarify` is not available or the user asks for immediate delivery, include "Optional questions" so they can refine later.

10. **Deliver ready to copy and paste.** The prompt must go inside a markdown code block (```) so the user can copy it with a single click. Text outside the block is explanation; the usable prompt goes inside the block.

## Tool Usage

- Use `clarify` when the original prompt's ambiguity is critical and there are multiple reasonable interpretations that change the result.
- Do not use `clarify` for minor ambiguities that can be resolved with a documented assumption.
- If `clarify` is not available, document Assumptions and Optional questions in the response.

## Response Format

Deliver in this order:

1. **Improved version** — the rewritten prompt inside a markdown code block (```). Ready to copy with a single click.
2. **Alternative version** (if applicable) — a second version inside its own code block. Omit if the original is already optimal in a single approach.
3. **Assumptions** (if applicable) — brief list of what was assumed to resolve ambiguities. Plain text, no code block.
4. **Optional questions** (if applicable) — concrete questions whose answers would significantly improve the prompt. Plain text, no code block.

Language rule: if the original prompt is in Spanish, respond in Spanish. If it is in English, respond in English.

## Example

**Original prompt:**

> necesito un script que lea csv y haga gráficos

**Improved version:**

```
Write a Python script that reads a CSV file and generates charts from its data.

Requirements:
- Read the file from a path provided as an argument.
- Automatically detect the numeric columns.
- Generate a line or bar chart for each numeric column.
- Save the charts as PNG files in an `output/` directory.
- Use pandas and matplotlib.

Acceptance criteria:
- Handle CSV files with UTF-8 and Latin-1 encodings.
- Handle null values by skipping them without breaking.
- Show a progress bar if the file has more than 1000 rows.
```

**More technical version:**

```
Python CLI script. Args: --input <path>, --output <dir>, --format png|svg.
Read CSV with pandas, numeric columns → matplotlib lineplot/barplot.
Encoding: UTF-8 with Latin-1 fallback. Nulls → dropna per column.
>1000 rows → tqdm progress bar. Output: PNG/SVG in output dir.
```

**Assumptions:**

- Python is assumed as the language (the most common for data work).
- Line/bar charts are assumed. If other chart types are needed (scatter, pie), specify.

## Pitfalls

- **Over-engineering simple prompts.** A 3-line prompt does not need 5 sections. If the direct version is clear, deliver it and move on.
- **Inventing requirements to "help".** Adding features, technologies, or criteria the user never mentioned changes the intent. What they did not say, do not assume.
- **Assuming too much instead of asking.** If the ambiguity changes the outcome significantly, use `clarify` instead of picking an interpretation and moving on. Assumptions are for minor ambiguities, not design decisions.
- **Stripping jargon that looks vague but is precise.** Domain-specific terms the user used may be exactly right in their context — preserve them.
- **Ignoring the language of the original.** Responding in English when the prompt was in Spanish (or vice versa) breaks the skill's usefulness for the user.
- **Delivering the prompt as plain text without a code block.** A multi-line prompt outside a code block is hard to copy — the user has to select it by hand. Always inside ``` for one-click copy.
- **Over-specifying until the prompt is single-use.** If the user wanted a reusable template, don't turn it into a prompt that only works for one narrow scenario.

## Verification

- [ ] Main intent of the original prompt understood and preserved.
- [ ] No invented requirements.
- [ ] Technical terms preserved exactly as written.
- [ ] Section structure only when it adds clarity.
- [ ] Tone adjusted to context (technical, design, analysis, general).
- [ ] Alternative version included when it adds value.
- [ ] Assumptions documented if there was ambiguity.
- [ ] `clarify` used when the ambiguity was critical (or the reason documented).
- [ ] Prompt delivered inside a markdown code block for easy copying.
- [ ] Result ready to copy and paste.
- [ ] Response language matches the original prompt's language.