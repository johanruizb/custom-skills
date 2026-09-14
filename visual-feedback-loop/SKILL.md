---
name: visual-feedback-loop
description: "Use whenever a change affects what the user will see (UI, layout, styling, charts, reports, PDFs, generated images) or the user provides a screenshot, mockup, or reference URL of how something should look. Enforces a closed visual feedback loop: capture the real output, compare it against the reference, close every delta, and show evidence before claiming the change is done. Triggers: 'no se ve como lo pedí', 'hazlo como esta imagen', 'verifícalo visualmente'."
license: MIT
metadata:
  author: johanruizb, Hermes Agent
  version: "1.0.0"
  platforms: [linux, macos, windows]
  hermes:
    tags: [visual-verification, screenshot, design-fidelity, ui-qa, feedback-loop, harness-agnostic]
    related_skills: [investigate-before-edit]
---

# Visual Feedback Loop

## Overview

A change can pass every test and still not look like what the user asked for. Visual properties are decided by the rendered result — cascades, overrides, media queries, layout interactions, fonts, the renderer — not by the values written in the code. Reading your own diff cannot tell you how it looks.

The only valid evidence is a **capture**: a frame of the real, running artifact. This skill runs every visual change through a closed loop:

```
contract → capture → compare → fix → capture → … → green
```

**Iron law:**

```
Capture, compare, and close every delta before claiming the change is done.
```

"Should look right" is a guess. A capture compared against the reference is the claim.

## When to Use

- The user provides an image, mockup, screenshot, or reference URL of how something should look.
- The user describes a target look in words — spacing, colors, layout, typography, style — and expects it honored.
- The change touches anything the user will see: web/desktop/mobile UI, charts, reports, PDFs, emails, generated images, terminal output.
- The user says it does not look like what they asked for.

Don't use when the change has no visual surface (pure logic, data, backend, config).

## Harness Adaptation

Map capabilities before starting. Do not assume a tool exists. If a needed capability is missing, say so and adapt — never substitute a guess for a check.

| Capability | Preferred | Fallback |
|---|---|---|
| Drive a browser, screenshot | `agent-browser` skill | Playwright / Puppeteer / headless Chrome |
| View images | multimodal file read | see *Can you see images?* |
| Run the app / render the artifact | shell | — |
| Export a non-web artifact to an image | render command (`pdftoppm`, ImageMagick, chart export API, terminal screenshot) | ask the user for a capture |
| Ask the user | conversation | — |

**Can you see images?** Decide this explicitly; it changes what "verified" means:

- **Yes** — compare captures against the reference directly.
- **No** — say so before starting. Verify numerically where possible (see *Numeric fallback*) and label the evidence as *measured, not seen*. Hand the final visual judgment to the user with the capture attached. Never claim a visual match you could not see.

## Phase 1 — Write the Visual Contract

Turn every reference into a checklist of concrete, observable attributes. An image held as a vibe drifts; a written contract is checkable, survives context compaction, and gives the compare phase something binary to test.

For each reference:

- **Image / mockup** — inspect it and record per region: layout and structure, spacing, alignment, colors (hex where readable), typography (size, weight, family), radii, borders, shadows, iconography, visible states.
- **Reference URL** — capture it yourself; it is also a reference.
- **Text description** — derive the same checklist; mark anything you had to assume.

Separate **chrome** (layout, spacing, colors, typography) from **content** (text, data, images). Chrome must match; content may legitimately differ.

Example contract:

```
- Header: logo left, nav right, 24px gap, 56px tall, 1px bottom border #E5E7EB
- Cards: 3-up grid, 16px gap, 12px radius, subtle shadow
- Primary button: #2563EB, 14px/600 white label, 8px radius, 36px tall
- States to check: default, button hover, empty state (centered message)
- Viewport: 1440×900, light theme
```

Confirm with the user only when an ambiguity would change the work (an unknown exact color, breakpoint, or behavior). Otherwise state the contract and proceed.

**Completion criterion:** every reference has a checklist of checkable attributes, and the states, viewports, and themes to capture are named. Checkable = two people looking at one capture can answer yes or no per line.

## Phase 2 — Baseline

When the view already exists, capture the current state before editing. It becomes the *before* in the report and the point to revert to if the loop stalls.

**Completion criterion:** baseline capture exists, or the view is new and there is nothing to capture.

## Phase 3 — Implement

Make the change. Keep the contract visible while editing; if the implementation must deviate from it, note the deviation for the compare phase.

## Phase 4 — Capture

- Run the real artifact — dev server, render command, built app — not a hand-made approximation of it.
- Capture every state named in the contract: route/screen, viewport, theme, and interactive state (default, hover, focus, open, loading, empty, error, long content).
- Match the reference's viewport and aspect ratio when known; if unknown, state the viewport you used. A viewport mismatch manufactures deltas that do not exist.
- Capture fresh: reload past caches, confirm the served build actually contains your change. Stale dev servers and failed hot-reloads are a common source of false greens.

**Completion criterion:** a capture exists for every contract state, from the same build the user will see.

## Phase 5 — Compare (the loop)

Put the capture and the reference side by side **in the same step**, and re-open the reference — never compare against your memory of it, which drifts toward what you just built.

Write the **delta list**: one line per mismatch — location, observed, expected.

```
- Card gap: observed 24px, expected 16px
- Button radius: observed 4px, expected 8px
- Hover: no visual change, expected darkening
```

Rules of the loop:

- Every mismatch is a line. "Looks close" is not a line. The loop goes **green** only when the list is empty.
- Ignore font antialiasing and sub-pixel rendering differences; they are not layout.
- Fix the deltas, then capture again. One **lap** = one pass of capture → compare → fix.
- If the same delta survives **three laps**, stop and escalate: show both captures, state your hypothesis, ask. Do not keep flailing.
- If the artifact fails to render, that is the first delta. A blank frame is never done.

**Completion criterion:** the delta list is empty, or every remaining line is an explicitly stated, agreed deviation (content differences, data you do not have, out-of-scope states).

## Phase 6 — Evidence Report

Report with artifacts, not beliefs:

- The final capture(s) — path or attachment — and the reference.
- The delta list result: empty, or the accepted deviations with the reason.
- What could not be verified: unreachable states, missing data, a harness that cannot view images.

"Captured 1440×900, five deltas closed, none remaining" is a report. "It should look like you asked" is not.

## Numeric fallback (when you cannot see captures)

Gather this evidence and label it as *measured, not seen*:

- `getComputedStyle(el)` for the contract's colors, fonts, radii, borders.
- `getBoundingClientRect()` and offset measurements for layout, spacing, alignment.
- Rendered widths/heights and overflow checks per breakpoint.

Then hand the captures to the user for the final visual call and ask them to report deltas.

## Common Pitfalls

1. **"The code sets the right values, so it renders correctly."** Cascades, specificity, global styles, media queries, parent layout, `z-index`, and overflow decide the result. Only the capture answers.
2. **Comparing against memory.** Re-open the reference every lap; memory of it warps toward your own output.
3. **Capturing the wrong state.** The default view is not the hover, empty, loading, or error state the contract named; the right state at the wrong viewport or theme is a different picture.
4. **Stale capture.** Hot reload did not apply, the asset was cached, the wrong port or branch is served. Confirm the change is in the served build before trusting a green.
5. **Accepting "close enough".** Close is a delta with no line written.
6. **Chasing rendering noise.** Antialiasing, font rasterization, and scrollbar differences are not deltas; do not "fix" them.
7. **Bundling fixes between laps.** Change only what the current delta list names, or the next capture cannot attribute what moved.
8. **Losing the reference.** After a compaction an image may drop from context; the written contract is the durable copy. Rebuild from it, and ask for the image again if the contract is insufficient.
9. **Delegating the comparison to a blind pair of eyes.** A subagent that cannot see images returns the same guess you had. If a subagent captures, the capture comes back to a viewer.
10. **Claiming green on a blank or broken render.** A failed render is the loudest delta.

## Completion Checklist

- [ ] Visual contract written: attributes, states, viewports, themes
- [ ] Baseline captured for existing views
- [ ] Captures taken from the real build, fresh, at every contract state
- [ ] Comparison made against the reference re-opened this lap
- [ ] Delta list empty, or remaining deviations stated and accepted
- [ ] Evidence shown: final captures + reference
- [ ] Limitations stated: unviewable captures, unreachable states, missing data
