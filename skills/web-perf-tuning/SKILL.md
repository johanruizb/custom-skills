---
name: web-perf-tuning
description: "Use when a web app feels slow, heavy, laggy, or janky in normal use (\"se siente pesada\", \"no fluye\", stutters on scroll or input), or the user asks to optimize frontend/UI performance, make an interface more fluid, speed up page load, or cut bundle size. For mature apps of any stack (React/Next, Vue/Nuxt, Angular, Svelte, vanilla): records a baseline first, fixes one dominant bottleneck per lap using per-stack playbooks, and verifies every fix with before/after numbers."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [performance, frontend, web, jank, bundle, profiling, optimization]
    related_skills: [codebase-audit]
---

# Web Performance Tuning

Restore fluidity to a web app that feels heavy. Built for apps already far along — working code, but the flow feels wrong: slow to appear, sluggish to interact, janky to scroll. The method finds what *specifically* is heavy instead of guessing, and fixes in order of measured impact.

Two parts:

- **Core method** (this file): the three layers, and the loop baseline → bottleneck → fix → verify. Stack-agnostic.
- **Stack playbooks** (`references/<stack>.md`): profiling tools, code sweeps, and ranked fixes for one stack. Exactly one is loaded per run, for the detected stack.

Uses the harness's file, shell, and user-question tools. Where a step needs a real browser, it hands the user an exact recipe and asks for the numbers back.

## When to Use

- The app "feels heavy", "doesn't flow", lags on input, or stutters while scrolling or animating.
- User asks to optimize or speed up a web UI, make it more fluid, cut load time, or reduce bundle size.
- A mature app needs a performance pass before shipping, or fluidity regressed over time.

Don't use for:

- Whole-codebase audits hunting bugs and security too — use `codebase-audit` (its performance review is static; this skill measures the running app).
- Backend-only tuning (queries, API latency). The network *waterfall* is in scope; fixing the server behind it is not.
- Greenfield projects with no symptoms yet — apply performance best practices directly while building.

## The three layers

Every finding belongs to one of three layers. Different symptoms, different tools, different fixes — naming the layer comes before any fix.

| Layer | What the user says | What is actually happening | Measured by |
|---|---|---|---|
| **Load** — getting pixels on screen | "tarda en cargar", blank screen, long spinner | Network **waterfall** (sequential requests), oversized first-load JS, render-blocking resources | Lighthouse (LCP, TTFB), build size report, Network tab |
| **Main thread** — work that blocks input | "se siente pesada", clicks do nothing, typing lags | **Long tasks** (>50 ms) of script/parse/GC pinning the thread | DevTools Performance: long-task list, Scripting ms |
| **Render churn** — framework/DOM work per interaction | "se traba al hacer scroll", UI updates sluggishly | Re-render storms, unvirtualized lists, layout thrashing, unthrottled handlers | Framework profiler + DevTools, dropped frames |

One complaint usually spans all three with one dominant layer. The method surfaces the dominant one before any fix is chosen.

## The method: laps

A **lap** is one bottleneck taken from fix to verified number. Laps run in impact order; each lap re-ranks what remains.

### Phase 1 — Orient

1. Detect the stack: read `package.json` (dependencies, scripts), the entry point, and the router. Note the data layer (React Query, Pinia, RxJS, …) — it owns several common bottlenecks.
2. Pin the worst flow as a **scenario**: the exact page plus action that feels worst ("open the dashboard, then type in the filter"). Ask the user when their report doesn't already name one. A run without a scenario is a generic review, and a generic review cannot verify anything.
3. Map each complaint to a layer hypothesis with the table above.

Done when the case line is written:

> Case: Next.js + React Query app. Worst flow: dashboard → type in the table filter. Symptoms: main thread (typing lags), some load (5 s LCP).

### Phase 2 — Baseline

Record numbers before touching code — every later claim of improvement compares against these.

Agent-measurable:

- Run the project's production build (its own script in `package.json`). Record total bundle, first-load JS per route, and the 5 largest chunks/deps.
- If a dev server can run: `npx lighthouse <url> --output=json --chrome-flags="--headless"` for LCP, TTFB, and total blocking time. If it can't, ask the user for a PageSpeed Insights run on the deployed URL.

Human-measured, for runtime symptoms — hand the user this recipe and ask for the numbers back:

> Chrome DevTools → Performance. Enable CPU 4× slowdown in the panel settings, click Record, perform the scenario once, stop. Report back:
> 1. Summary split: Scripting / Rendering / Painting ms.
> 2. Top 3 long tasks (red markers): duration + initiating function (Call Tree or Bottom-Up).
> 3. If jank on scroll/animation: FPS meter reading (Cmd/Ctrl+Shift+P → "Show frames per second meter").

The stack playbook names its framework profiler (React DevTools, Vue Devtools, Angular DevTools) — hand that recipe too when it applies.

Done when every Phase-1 symptom has a baseline number and its source (build report, Lighthouse, or user-provided trace). A lap started without a baseline number cannot be verified in Phase 5 — it never started.

### Phase 3 — Diagnose

1. Run the **static sweep** from the stack playbook (code findings, no browser).
2. Merge sweep findings with baseline numbers into one ranked list. Rank by user-perceived impact on the scenario: the dominant long task and the first-load JS of the slow route outrank minor smells.
3. Name the **dominant bottleneck** — the single fix with the largest expected effect.

Done when the ranked list gives every entry a layer and evidence — a number with its source, or a `file:line` from the sweep. The head of the list is the next lap.

### Phase 4 — Fix

Load `references/<stack>.md` and apply the fix for the named bottleneck. One bottleneck per lap: a lap that ships several fixes at once cannot attribute its before/after.

Done when the build passes and the fix's rationale cites the finding it targets ("long task 320 ms initiated by Table render → virtualize the list").

### Phase 5 — Verify, then lap again

1. Re-measure with the same method as the baseline: same build command; same user recipe for runtime numbers.
2. Record a **ledger** row, before → after:
   - Improved: keep the fix, cross the bottleneck off, return to Phase 3 for the next lap.
   - Flat or worse: **revert**. A fix that adds complexity without a measured win is itself a regression. Re-diagnose — the finding was misread, or the fix missed it.

Done when the user confirms the scenario feels better, or the rank is empty. The ledger is the deliverable.

## Stack playbooks

| Detected in package.json | Playbook |
|---|---|
| `react`, `next`, `react-dom` | `references/react.md` |
| `vue`, `nuxt` | `references/vue.md` |
| `@angular/core` | `references/angular.md` |
| `svelte`, `@sveltejs/kit` | `references/svelte.md` |
| none of the above (server-rendered, htmx, plain JS) | `references/vanilla.md` |

Load exactly one. The **DOM/CSS layer** in `references/vanilla.md` applies to every stack — the framework playbooks point back to it for scroll jank and animation cases instead of repeating it.

## The ledger

The run's final report, one row per lap:

| Lap | Bottleneck | Layer | Evidence | Fix | Before → After | Kept/Reverted |
|---|---|---|---|---|---|---|

Below it: the final case line, and the remaining ranked candidates if the rank isn't empty. A fix without a before/after row appears in the ledger as unverified, never as a win.