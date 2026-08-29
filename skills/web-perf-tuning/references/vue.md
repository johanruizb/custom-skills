# Vue / Nuxt playbook

Vue's reactivity is dependency-tracked: a component re-renders only when values it actually read change. Re-render storms are rarer than in React — the weight usually sits in *deep reactivity* over big data, watchers, and the DOM layer.

## Profile with

- **Vue Devtools** (extension): Timeline tab records reactive events and component renders against the scenario; Inspector shows each component's state and props. Recipe: Timeline → Record → perform the scenario → stop → report the densest event clusters and which components rendered.
- **Chrome Performance** (core recipe, Phase 2) for long tasks.
- **Bundle**: Nuxt — `nuxi analyze` renders a per-module size treemap. Vite — build with `rollup-plugin-visualizer`.

## Static sweep

| Look for | Means |
|---|---|
| `ref(hugeObject)` / `reactive(bigArray)` for large, mostly-read data (tables, trees, chart/map data) | Deep proxy over every property — `shallowRef` + replace on change, or `markRaw` |
| `watch(…, { deep: true })` on large state | Full-object traversal on every change — watch a narrow key, or flatten |
| Big `v-for` with no virtualization (`vue-virtual-scroller`, `@tanstack/vue-virtual`) | Unvirtualized list |
| `v-for` without `:key`, or `:key="index"` on reorderable data | Remount churn |
| Expensive method calls in templates (`{{ compute(rows) }}`) | Re-evaluated on every render of that component — `computed` |
| Side effects or mutations inside `computed` | Cascading invalidations — move to `watch`/`watchEffect` |
| One big store read by many components, plus `store.$subscribe` / `watch(store, …)` | Any change re-renders or notifies all readers — split into per-slice stores, subscribe narrowly |
| All views statically imported in the router | First bundle carries every page — `() => import('./views/…')` |
| Unthrottled `scroll`/`input` listeners; event-bus (`mitt`) handlers doing heavy work | Work per event — rAF-gate it (see `references/vanilla.md`) |
| Nuxt: large payload, plugins running client-side without need | Payload/plugin weight — extract less state, split plugins with `.server` / `.client` suffixes |

## Ranked bottlenecks

| Signature | Bottleneck | Fix |
|---|---|---|
| Long tasks when big data loads or mutates; Timeline dense with reactive events | Deep reactivity on large data | `shallowRef` + `triggerRef`; `markRaw` for third-party instances |
| Long task on list interactions | Unvirtualized list | Virtualize; keyed `v-for` |
| Wide component renders in Timeline after one small change | Over-broad reactive reads | Narrow reads and `computed`s; split components |
| Slow input/scroll handlers | Unthrottled listeners | rAF-gate, passive listeners (`references/vanilla.md`) |
| Large first-load JS; route chunks missing | Eager imports | Lazy routes; code-split heavy components |
| Slow LCP: image/font weight | Blocking media | `@nuxt/image` or lazy + `srcset`; font preload + `font-display: swap` |
| Dropped frames on scroll/animation | DOM/CSS layer | `references/vanilla.md` |