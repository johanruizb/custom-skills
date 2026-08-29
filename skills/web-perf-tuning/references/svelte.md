# Svelte / SvelteKit playbook

Svelte compiles reactivity away — runtime overhead is small, so the weight usually sits in large reactive data, big each-blocks, transitions that trigger layout, and the DOM layer.

## Profile with

- **Chrome Performance** (core recipe, Phase 2) — the main tool; Svelte work shows as component update functions in the flame chart.
- **`svelte-check`** — cheap pass for state/a11y warnings that hint at reactive misuse.
- **Bundle**: SvelteKit uses Vite — `vite build` prints per-route chunk sizes; build once with `rollup-plugin-visualizer` for the treemap.

## Static sweep

| Look for | Means |
|---|---|
| Svelte 5: `$state` on huge arrays/objects | Deep reactive proxy over big data — `$state.raw` for write-rarely data |
| Svelte 4: `$:` chains that recompute wide on each change | Cascade re-computation — narrow the statements, split components |
| Big `{#each}` without a `key`; no virtualization | Remount churn / unvirtualized list (`@tanstack/svelte-virtual`, `svelte-virtual-scroll-list`) |
| One big `writable` store read by many components | Every change re-renders all readers — split into per-slice stores |
| Whole-library imports; heavy routes/components statically imported | First-bundle bloat — dynamic `import()` for the heavy pieces |
| Unthrottled scroll/input work inside actions (`use:…`) | Per-event work — rAF-gate it (see `references/vanilla.md`) |
| Transitions animating layout properties (`top`, `width`, `margin`) | Layout every frame — animate `transform`/`opacity` instead |

## Ranked bottlenecks

| Signature | Bottleneck | Fix |
|---|---|---|
| Long tasks when big data mutates | Deep reactivity on large data | `$state.raw` (Svelte 5) / split stores; patch narrow slices |
| Long task on list render/scroll | Unvirtualized list | Virtualize + keyed `{#each}` |
| Dropped frames during transitions/scroll | Layout-triggering transitions; DOM layer | `transform`/`opacity`; `references/vanilla.md` |
| Large first bundle | Eager imports | Dynamic `import()` for heavy routes and components |
| Slow LCP: media/fonts blocking | Blocking media | Preload; `loading="lazy"` + `srcset`; `font-display: swap` |